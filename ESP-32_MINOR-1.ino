#include <Arduino.h>
#include "BluetoothSerial.h"

// Create a Bluetooth Serial Object
BluetoothSerial serialBT;

// Motor PWM channels and pins
#define R1PWM 19  // Example: PWM control for motor driver input
#define R2PWM 21
#define L1PWM 23
#define L2PWM 22

// Channels
#define R1 0
#define R2 1
#define L1 2
#define L2 3

// Speed value
//changed the val from 150 to 255
int Speed = 150; // 0-255 range for 8-bit resolution

void setup() {
  Serial.begin(115200);

  // Initialize Bluetooth
  if (!serialBT.begin("Lab Assistant")) {
    Serial.println("An error occurred initializing Bluetooth");
  } else {
    Serial.println("Bluetooth initialized. Pair and send commands.");
  }

  // PWM setup: channel, frequency, resolution
  ledcSetup(R1, 5000, 8);
  ledcSetup(R2, 5000, 8);
  ledcSetup(L1, 5000, 8);
  ledcSetup(L2, 5000, 8);

  // Attach PWM channels to GPIO pins
  ledcAttachPin(R1PWM, R1);
  ledcAttachPin(R2PWM, R2);
  ledcAttachPin(L1PWM, L1);
  ledcAttachPin(L2PWM, L2);

  // Initially stop all motors
  stopMotors();
}

void loop() {
  if (serialBT.available()) {
    char btSignal = serialBT.read();

    Serial.print("Received Command: ");
    Serial.println(btSignal);

    switch (btSignal) {
      case 'L':
        moveForward();
        break;
      case 'R':
        moveBackward();
        break;
      case 'F':
        turnLeft();
        break;
      case 'B':
        turnRight();
        break;
      case 'S':
        stopMotors();
        break;
      case '+':  // Speed up
        Speed = min(Speed + 10, 255);
        Serial.print("Speed Increased to ");
        Serial.println(Speed);
        break;
      case '-':  // Slow down
        Speed = max(Speed - 10, 0);
        Serial.print("Speed Decreased to ");
        Serial.println(Speed);
        break;
      default:
        Serial.println("Unknown command");
        break;
    }
  }
}

void moveForward() {
  Serial.println("Moving Forward");
  ledcWrite(R1, Speed);
  ledcWrite(R2, 0);
  ledcWrite(L1, Speed);
  ledcWrite(L2, 0);
}

void moveBackward() {
  Serial.println("Moving Backward");
  ledcWrite(R1, 0);
  ledcWrite(R2, Speed);
  ledcWrite(L1, 0);
  ledcWrite(L2, Speed);
}

void turnLeft() {
  Serial.println("Turning Left");
  ledcWrite(R1, 0);
  ledcWrite(R2, Speed);
  ledcWrite(L1, Speed);
  ledcWrite(L2, 0);
}

void turnRight() {
  Serial.println("Turning Right");
  ledcWrite(R1, Speed);
  ledcWrite(R2, 0);
  ledcWrite(L1, 0);
  ledcWrite(L2, Speed);
}

void stopMotors() {
  Serial.println("Stopping Motors");
  ledcWrite(R1, 0);
  ledcWrite(R2, 0);
  ledcWrite(L1, 0);
  ledcWrite(L2, 0);
}
