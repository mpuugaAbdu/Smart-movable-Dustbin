#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <string.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);
Servo myServo;

// Motor A
const int in1 = 11;
const int in2 = 12;

// Motor B
const int in3 = 13;
const int in4 = 14;  // A0

// Motor speed pins
const int ena = 5;
const int enb = 6;

const int motorSpeed = 80;

// Voice module pulse inputs
const int backwardVoicePin = 7;
const int forwardVoicePin = 8;

// Servo control
const int servoControlPin = 3;  
const int servoPin = 9;
int servoPosition = 0;
bool lastServoInput = LOW;

// Ultrasonic Sensor 1 - used when moving backward
const int trig1 = 0;
const int echo1 = 1;

// Ultrasonic Sensor 2 - used when moving forward
const int trig2 = 10;
const int echo2 = 2;

// Stop distance in centimeters
const int obstacleDistance = 20;

bool lastForwardPulse = LOW;
bool lastBackwardPulse = LOW;

enum MotionMode
{
  STOPPED,
  MOVING_FORWARD,
  MOVING_BACKWARD
};

MotionMode motionMode = STOPPED;

char lastLcdLine1[17] = "";
char lastLcdLine2[17] = "";

void setup()
{
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  pinMode(ena, OUTPUT);
  pinMode(enb, OUTPUT);

  pinMode(forwardVoicePin, INPUT);
  pinMode(backwardVoicePin, INPUT);
  pinMode(servoControlPin, INPUT);

  pinMode(trig1, OUTPUT);
  pinMode(echo1, INPUT);

  pinMode(trig2, OUTPUT);
  pinMode(echo2, INPUT);

  digitalWrite(trig1, LOW);
  digitalWrite(trig2, LOW);

  myServo.attach(servoPin);
  myServo.write(0);
  delay(500);
  myServo.detach();

  lcd.init();
  lcd.backlight();

  stopCar();
  showStatus("Robot stopped", "Waiting command");
}

void loop()
{
  bool forwardPulse = digitalRead(forwardVoicePin);
  bool backwardPulse = digitalRead(backwardVoicePin);

  if (forwardPulse == HIGH && lastForwardPulse == LOW)
  {
    motionMode = MOVING_FORWARD;
    showStatus("Forward command", "Sensor 2 active");
  }

  if (backwardPulse == HIGH && lastBackwardPulse == LOW)
  {
    motionMode = MOVING_BACKWARD;
    showStatus("Backward command", "Sensor 1 active");
  }

  lastForwardPulse = forwardPulse;
  lastBackwardPulse = backwardPulse;

  checkObstacleAndMove();

  // Servo works only when robot is stationary
  if (motionMode == STOPPED)
  {
    handleServo();
  }
}

void handleServo()
{
  bool servoInput = digitalRead(servoControlPin);

  if (servoInput != lastServoInput)
  {
    myServo.attach(servoPin);

    if (servoInput == HIGH)
    {
      showStatus("Servo opening", "Moving to 90 deg");

      for (int pos = servoPosition; pos <= 90; pos++)
      {
        myServo.write(pos);
        delay(15);
      }

      servoPosition = 90;
    }
    else
    {
      showStatus("Servo closing", "Moving to 0 deg");

      for (int pos = servoPosition; pos >= 0; pos--)
      {
        myServo.write(pos);
        delay(15);
      }

      servoPosition = 0;
    }

    delay(300);
    myServo.detach();

    lastServoInput = servoInput;
    showStatus("Robot stopped", "Waiting command");
  }
}

void checkObstacleAndMove()
{
  if (motionMode == MOVING_FORWARD)
  {
    int distance2 = getDistanceCM(trig2, echo2);

    if (distance2 > 0 && distance2 <= obstacleDistance)
    {
      stopCar();
      motionMode = STOPPED;
      showStatus("Front obstacle", "Robot stopped");
      return;
    }

    driveForward(motorSpeed, motorSpeed);
    showStatus("Moving forward", "Path clear");
  }

  else if (motionMode == MOVING_BACKWARD)
  {
    int distance1 = getDistanceCM(trig1, echo1);

    if (distance1 > 0 && distance1 <= obstacleDistance)
    {
      stopCar();
      motionMode = STOPPED;
      showStatus("Rear obstacle", "Robot stopped");
      return;
    }

    driveBackward(motorSpeed, motorSpeed);
    showStatus("Moving backward", "Path clear");
  }

  else
  {
    stopCar();
  }
}

int getDistanceCM(int trigPin, int echoPin)
{
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 20000);

  if (duration == 0)
  {
    return -1;
  }

  int distance = duration * 0.034 / 2;
  return distance;
}

void driveForward(int leftSpeed, int rightSpeed)
{
  analogWrite(ena, leftSpeed);
  analogWrite(enb, rightSpeed);

  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);

  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
}

void driveBackward(int leftSpeed, int rightSpeed)
{
  analogWrite(ena, leftSpeed);
  analogWrite(enb, rightSpeed);

  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);

  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
}

void stopCar()
{
  analogWrite(ena, 0);
  analogWrite(enb, 0);

  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);

  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
}

void printLcdLine(int row, const char *text)
{
  lcd.setCursor(0, row);

  int column = 0;

  while (text[column] != '\0' && column < 16)
  {
    lcd.print(text[column]);
    column++;
  }

  while (column < 16)
  {
    lcd.print(' ');
    column++;
  }
}

void showStatus(const char *line1, const char *line2)
{
  if (strcmp(line1, lastLcdLine1) == 0 &&
      strcmp(line2, lastLcdLine2) == 0)
  {
    return;
  }

  printLcdLine(0, line1);
  printLcdLine(1, line2);

  strncpy(lastLcdLine1, line1, 16);
  strncpy(lastLcdLine2, line2, 16);

  lastLcdLine1[16] = '\0';
  lastLcdLine2[16] = '\0';
}