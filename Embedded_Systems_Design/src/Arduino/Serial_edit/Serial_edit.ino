String Speed;
char  LorR;
int  i, s;
// 1119 추가
int motorA1 = 3;
int motorA2 = 11;
int motorB1 = 5;
int motorB2 = 6;

unsigned int motorA_SPEED = 0, motorB_SPEED = 0;
boolean motorA_DIR = 0, motorB_DIR = 0;

byte DataToRead[6];

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(motorA1, OUTPUT);
  pinMode(motorA2, OUTPUT);
  pinMode(motorB1, OUTPUT);
  pinMode(motorB2, OUTPUT);
}

void loop() {
  DataToRead[5] = '\n';
  Serial.readBytesUntil(char(13), DataToRead, 5);
  
/* For Debugging, send string to RPi */
  for (i = 0; i < 6; i++) {
    Serial.write(DataToRead[i]);
    if (DataToRead[i] == '\n') break;
  }
/* End of Debugging */

  LorR = DataToRead[0];
  Speed = "";
  for (i = 1; (DataToRead[i] != '\n') && (i < 6); i++) {
    Speed += DataToRead[i];
  }
  s = Speed.toInt();

  if (LorR == 'L') {
    // Turn left wheel with speed s
    if (s < 0) {
      motorA_DIR = HIGH;
    }
    else {
      motorA_DIR = LOW;
    }
    motorA_SPEED = abs(s);
    digitalWrite(motorA1, motorA_DIR);
    analogWrite(motorA2, motorA_SPEED);
  }
  
  else if (LorR == 'R') {
    // Turn right wheel with speed s  
    if (s < 0) {
      motorB_DIR = HIGH;
    }
    else {
      motorB_DIR = LOW;
    }
    motorB_SPEED = abs(s);
    analogWrite(motorB1, motorB_SPEED);
    digitalWrite(motorB2, motorB_DIR);
  }
  
  else if (LorR == 'S') {
    // Stop Motors
    digitalWrite(motorA1, LOW);
    analogWrite(motorA2, 0);
    analogWrite(motorB1, 0);
    digitalWrite(motorB2, LOW);

    delay(500);
  }
}
