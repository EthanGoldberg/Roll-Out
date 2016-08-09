#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 12
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
int LED = 13;
char getstr;
int Echo = A4;  
int Trig = A5; 
int in1 = 6;
int in2 = 7;
int in3 = 8;
int in4 = 9;
int ENA = 5;
int ENB = 10;
int FORWARD_SPEED = 110;
int LITE_TURN_SPEED=170;

int dist;
char const* stat;
float temp;
int response_code; // BASE = 0, READY = 1, ERROR = 2
char prev_adj; // Previous adjustment direction.  'r' = right, 'l' = left
int adj_count; // Actions since last adjustment.

int L_tracker = 0;
int M_tracker = 0;
int R_tracker = 0;

/* Writes car data to serial using established protocol. */
void inform(){
  Serial.print(stat);
  Serial.print("_");
  Serial.print(dist);
  Serial.print("_");
  Serial.print(temp);
  Serial.print("_");
  Serial.println(response_code);
}

/* Moves car forward.  Created by ELEGO. */
 void _mForward(){
  analogWrite(ENA,FORWARD_SPEED);
  analogWrite(ENB,FORWARD_SPEED);
  digitalWrite(in1,LOW);
  digitalWrite(in2,HIGH);
  digitalWrite(in3,LOW);
  digitalWrite(in4,HIGH);
}

/* Moves car backward.  Created by ELEGO. */
void _mBack(){
  analogWrite(ENA,FORWARD_SPEED);
  analogWrite(ENB,FORWARD_SPEED);
  digitalWrite(in1,HIGH);
  digitalWrite(in2,LOW);
  digitalWrite(in3,HIGH);
  digitalWrite(in4,LOW);
}

/* Turns car left at full speed.  Created by ELEGO. */
void _mleft(){
   digitalWrite(ENA,HIGH);
   digitalWrite(ENB,HIGH);
   digitalWrite(in1,LOW);
   digitalWrite(in2,HIGH);
   digitalWrite(in3,HIGH);
   digitalWrite(in4,LOW);
}

/* Turns car right at full speed.  Created by ELEGO. */
void _mright(){
   digitalWrite(ENA,HIGH);
   digitalWrite(ENB,HIGH);
   digitalWrite(in1,HIGH);
   digitalWrite(in2,LOW);
   digitalWrite(in3,LOW);
   digitalWrite(in4,HIGH);
}

/* Turns car left at reduced speed. */
void _leftlite(){
   analogWrite(ENA,LITE_TURN_SPEED);
   analogWrite(ENB,LITE_TURN_SPEED);
   digitalWrite(in1,LOW);
   digitalWrite(in2,HIGH);
   digitalWrite(in3,HIGH);
   digitalWrite(in4,LOW);
}

/* Turns car right at reduced speed. */
void _rightlite(){
   analogWrite(ENA,LITE_TURN_SPEED);
   analogWrite(ENB,LITE_TURN_SPEED);
   digitalWrite(in1,HIGH);
   digitalWrite(in2,LOW);
   digitalWrite(in3,LOW);
   digitalWrite(in4,HIGH);
}

/* Discrete step to turn car right until it reaches the next state. */
void rturn(){
    boolean lw = false;
    boolean mw = false;
    boolean rw = false;
    stat = "Turning right.";
    response_code = 0;
    inform();
    while (!lw || !mw || !rw){
      _mright();
      if (!digitalRead(2)) {
          lw = true;  
      }
      if (!digitalRead(4)) {
          mw = true;
      }
      if (!digitalRead(11)) {
          rw = true;  
      }
    }
    while(!digitalRead(2) || !digitalRead(4) || !digitalRead(11)) {
        _mright();
    }
    _mStop();
    response_code = 1;
    inform();
    response_code = 0;
}

/* Discrete step to turn car left until it reaches the next state. */
void lturn(){
    boolean lw = false;
    boolean mw = false;
    boolean rw = false;
    stat = "Turning left.";
    response_code = 0;
    inform();
    while (!lw || !mw || !rw) {
      _mleft();
      if (!digitalRead(2)) {
          lw = true;  
      }
      if (!digitalRead(4)) {
          mw = true;
      }
      if (!digitalRead(11)) {
          rw = true;  
      }
    }
    while(!digitalRead(2) || !digitalRead(4) || !digitalRead(11)) {
        _mleft();
    }    
    _mStop();
    response_code = 1;
    inform();
    response_code = 0;
}

/* Discrete step to turn car 180 degrees. */
void uturn(){
  if (digitalRead(2) || digitalRead(4) || digitalRead(11)) {
    stat = "Off track.";
    response_code = 2;
    inform();
    return;
  }
  
 if (adj_count <= 2) {
        if (prev_adj == 'r') {
            rturn();
        }
        else if (prev_adj == 'l') {
            lturn();
        }
    }
  else {
     rturn();
  }
}

/* Stops the car. */
void _mStop(){
   digitalWrite(ENA,LOW);
   digitalWrite(ENB,LOW);
}

 /* Ultrasonic distance measurement subfunction.  Written by ELEGO. */
int Distance_test(){
  digitalWrite(Trig, LOW);
  delayMicroseconds(5);
  digitalWrite(Trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(Trig, LOW);   
  float Fdistance = pulseIn(Echo, HIGH, 10000);
  Fdistance= Fdistance/58;       
  return (int)Fdistance;
}

/* Stops the car if there is an obstacle ahead. */
void handle_obstacle(){
  dist = Distance_test();
  if (dist != 0 && dist != 5 && dist <= 25) {
    stat = "Obstacle ahead.";
    response_code = 0;
    inform();
  }
  while (dist != 0 && dist != 5 && dist <= 25) {
    _mStop();
    inform();
    delay(500);
    sensors.requestTemperatures();
    temp = sensors.getTempFByIndex(0);
    dist = Distance_test();
  } 
}

/* Line tracking measurement */
void line_tracker_update(){
    L_tracker = digitalRead(2);
    M_tracker = digitalRead(4);
    R_tracker = digitalRead(11);
}

/* Discrete step to drive car forward until it reaches the next state.
 *  Based on function written by ELEGO.
 */
void track(){
  /* If there is initially no path to track, guess the
   *  correct action based on most recent adjustment.
   *  If there is no recent adjustment, report an error.
  */
  line_tracker_update();
  if (!L_tracker && !M_tracker && !R_tracker) {
      if (adj_count <= 2) {
          if (prev_adj == 'r') {
              lturn();
          }
          else if (prev_adj == 'l') {
              rturn();
          }
      }
      else {
          stat = "Off course.";
          response_code = 2;
          inform();
          response_code = 0;
          return;
      }
  }

  stat = "Moving forward.";
  response_code = 0;
  inform();
  line_tracker_update();
  while(M_tracker){
    if(R_tracker==0&&L_tracker){
        prev_adj = 'l';
        adj_count = 0;
        _leftlite();
    }    
    else if(R_tracker&&(L_tracker==0)){
        prev_adj = 'r';
        adj_count = 0;
        _rightlite();
    }
    else{
        _mForward();
        handle_obstacle();
    }
    line_tracker_update();
  }
    _mForward();
    delay(250);
    line_tracker_update();
    while (R_tracker==0&&M_tracker==0&&L_tracker){
      _leftlite();
      line_tracker_update();
    }
    while (R_tracker&&M_tracker==0&&L_tracker==0){
      _rightlite();
      line_tracker_update();
    } 
    _mStop();
    response_code = 1;
    inform();
    response_code = 0;
}

/* Based on setup() function written by ELEGO. */
void setup(){
  pinMode(LED, OUTPUT);
  Serial.begin(9600);
  pinMode(Echo, INPUT);    
  pinMode(Trig, OUTPUT);  
  pinMode(in1,OUTPUT);
  pinMode(in2,OUTPUT);
  pinMode(in3,OUTPUT);
  pinMode(in4,OUTPUT);
  pinMode(ENA,OUTPUT);
  pinMode(ENB,OUTPUT);
  sensors.begin();
  sensors.setWaitForConversion(false);
  stat = "Waiting for instructions...";
  response_code = 0;
  inform();
  prev_adj = 'r';
  adj_count = 10;
  _mStop();
}

/* Based on loop() function written by ELEGO. */
void loop(){
 sensors.requestTemperatures();
 temp = sensors.getTempFByIndex(0);
 handle_obstacle();

 if (Serial.available() > 0){
   getstr=Serial.read();
   if(getstr=='f'){
      _mForward();
      delay(200);
      _mStop();
    }
    else if(getstr=='b'){
      _mBack();
      delay(200);
      _mStop();
    }
    else if(getstr=='l'){
      lturn();
    }
    else if(getstr=='r'){
      rturn();
    }
    else if (getstr=='u'){
      uturn();  
    }
    else if (getstr=='t'){
      track();
      adj_count += 1;
    }
    else if(getstr=='s'){
       _mStop();
       stat = "Stopped.";
       response_code = 1;
       inform();
       response_code = 0;
    }
    else if(getstr=='d'){
      stat = "Finished task";
      response_code = 1;
      inform();
      response_code = 0;
    }
    else if(getstr=='h'){
      stat = "Ready to go.";
      response_code = 1;
      inform();
      response_code = 0;  
    }
    else {
      stat = "Invalid command.";
      response_code = 0;
      inform();  
    }
 }
}

