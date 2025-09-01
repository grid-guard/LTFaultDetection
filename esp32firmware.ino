#include <WiFi.h>


void setup(){
pinMode(RELAY_PIN, OUTPUT); digitalWrite(RELAY_PIN, LOW);
WiFi.begin(WIFI_SSID, WIFI_PASS);
while(WiFi.status()!=WL_CONNECTED) delay(500);
mqtt.setServer(MQTT_HOST, MQTT_PORT); mqtt.setCallback(mqttCallback);
}


float readRMS(int pin, int ms){
int N = (FS * ms)/1000; if(N<200) N = 200; // safety
double sum2 = 0; for(int i=0;i<N;i++){ int ra = analogRead(pin); double x = (ra/4095.0)*3.3; // volts
x -= 1.65; // mid-bias
sum2 += x*x; delayMicroseconds( (int)(1e6/FS) ); }
double vrms = sqrt(sum2/N);
return vrms; // sensor calibration applied later
}


float calIrms(float adcVrms){
// TODO: set from calibration; example: 1.0 Vadc rms == 50 A rms
return adcVrms * 50.0;
}
float calVrms(float adcVrms){
// Example: 0.2 Vadc rms == 230 Vrms
return adcVrms * (230.0/0.2);
}


void publish(float v_rms, float i_rms, float pf, float thd_est, const char* status, float fprob){
char topic[128]; snprintf(topic,sizeof(topic),"telemetry/%s/%d",PANEL_ID,LINE_ID);
char payload[256];
unsigned long ts = millis();
snprintf(payload,sizeof(payload),
"{\"ts\":%lu,\"v_rms\":%.1f,\"i_rms\":%.1f,\"pf\":%.2f,\"thd_est\":%.1f,\"status\":\"%s\",\"fault_prob\":%.2f,\"lineId\":%d,\"panelId\":\"%s\"}",
ts,v_rms,i_rms,pf,thd_est,status,fprob,LINE_ID,PANEL_ID);
mqtt.publish(topic,payload);
}


void loop(){
ensureMqtt(); mqtt.loop();


float i_vrms_adc = readRMS(ADC_I, WINDOW_MS);
float v_vrms_adc = readRMS(ADC_V, WINDOW_MS);
float i_rms = calIrms(i_vrms_adc);
float v_rms = calVrms(v_vrms_adc);


// Simple heuristics
static float ema_i = 0; ema_i = 0.9*ema_i + 0.1*i_rms;
bool overload = (i_rms > 1.3*max(ema_i, 1.0));
bool openline = (i_rms < 0.2) && (v_rms > 180);


float fault_prob = overload?0.7:0.02; if(openline) fault_prob=0.9;
const char* status = (fault_prob>0.8)?"fault":((fault_prob>0.2)?"warning":"normal");


if((openline||overload)) trip_latched = true;
digitalWrite(RELAY_PIN, trip_latched ? HIGH : LOW); // HIGH ⇒ isolate


publish(v_rms,i_rms,0.95,5.0,status,fault_prob);
}
