#define STEP 8
#define EN 4
#define M1 5
#define M2 6
#define M3 7
char message = ' ';

void move(){
    digitalWrite(EN, LOW);delay(1);
    
    digitalWrite(STEP, LOW);delayMicroseconds(900);digitalWrite(STEP, HIGH);delayMicroseconds(700);
    digitalWrite(STEP, LOW);delayMicroseconds(500);digitalWrite(STEP, HIGH);delayMicroseconds(500);
    digitalWrite(STEP, LOW);delayMicroseconds(500);digitalWrite(STEP, HIGH);delayMicroseconds(500);
    digitalWrite(STEP, LOW);delayMicroseconds(700);digitalWrite(STEP, HIGH);delayMicroseconds(900);

    
    Serial.println("ok");
}



void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(EN, OUTPUT);pinMode(M1, OUTPUT);pinMode(M2, OUTPUT);pinMode(M3, OUTPUT);pinMode(STEP, OUTPUT);
  digitalWrite(M1, HIGH);digitalWrite(M2, HIGH);digitalWrite(M3, HIGH);digitalWrite(EN, HIGH);digitalWrite(STEP, HIGH);
  
}

void loop() {
  if(Serial.available())
    message = Serial.read();
    
  if (message == 'r')
    Serial.println("ready");    
  else if (message == 'm')
    move(); 
  else if (message == 's')
    digitalWrite(EN, HIGH);
    
  message = ' ';
}



