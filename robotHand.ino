#include <ESP32Servo.h>

// ======= QUICK SERVO ENABLES =======
#define USE_THUMB   true
#define USE_INDEX   true
#define USE_MIDDLE  true
#define USE_RING    true
#define USE_PINKY   true
// ===================================


const int abortPin = 0;     // BOOT button on ESP32 DevKit V1
const int step = 10;

// Create servo objects
Servo thumbServo;
Servo indexServo;
Servo middleServo;
Servo ringServo;
Servo pinkyServo;

// Pin assignments
const int THUMB_PIN = 32;
const int INDEX_PIN = 33;
const int MIDDLE_PIN = 25;
const int RING_PIN = 26;
const int PINKY_PIN = 27;

// Status strings
String thumbStatus = "";
String indexStatus = "";
String middleStatus = "";
String ringStatus = "";
String pinkyStatus = "";

void setup() {
  Serial.begin(9600);
  
  // Attach only the enabled servos
  if (USE_THUMB)  thumbServo.attach(THUMB_PIN);
  if (USE_INDEX)  indexServo.attach(INDEX_PIN);
  if (USE_MIDDLE) middleServo.attach(MIDDLE_PIN);
  if (USE_RING)   ringServo.attach(RING_PIN);
  if (USE_PINKY)  pinkyServo.attach(PINKY_PIN);

  // Initialize to open
  if (USE_THUMB)  thumbServo.write(0);
  if (USE_INDEX)  indexServo.write(0);
  if (USE_MIDDLE) middleServo.write(0);
  if (USE_RING)   ringServo.write(0);
  if (USE_PINKY)  pinkyServo.write(0);
}

void loop() {
  if (digitalRead(abortPin) == LOW) abortNow();
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    
    // Parse format: T:status,I:status,M:status,R:status,P:status
    parseStatuses(data);
    
    // Convert to servo angles
    if (USE_THUMB)  thumbServo.write(getAngle(thumbStatus));
    if (USE_INDEX)  indexServo.write(getAngle(indexStatus));
    if (USE_MIDDLE) middleServo.write(getAngle(middleStatus));
    if (USE_RING)   ringServo.write(getAngle(ringStatus));
    if (USE_PINKY)  pinkyServo.write(getAngle(pinkyStatus));
  }
}

void abortNow() {
  Serial.println("ABORT PRESSED — stopping servos.");
  if (USE_THUMB)  thumbServo.detach();
  if (USE_INDEX)  indexServo.detach();
  if (USE_MIDDLE) middleServo.detach();
  if (USE_RING)   ringServo.detach();
  if (USE_PINKY)  pinkyServo.detach();
  while (true) delay(100);
}

void parseStatuses(String data) {
  int startIdx = 0;
  int commaIdx = 0;
  
  while (commaIdx != -1) {
    commaIdx = data.indexOf(',', startIdx);
    String segment = (commaIdx == -1) ? data.substring(startIdx) : data.substring(startIdx, commaIdx);
    
    int colonIdx = segment.indexOf(':');
    if (colonIdx != -1) {
      String finger = segment.substring(0, colonIdx);
      String status = segment.substring(colonIdx + 1);
      
      if (finger == "T") thumbStatus = status;
      else if (finger == "I") indexStatus = status;
      else if (finger == "M") middleStatus = status;
      else if (finger == "R") ringStatus = status;
      else if (finger == "P") pinkyStatus = status;
    }
    
    startIdx = commaIdx + 1;
  }
}

int getAngle(String status) {
  if (status == "Straight" || status == "Not Swept") {
    return 0;
  } 
  else if (status == "Half Bent" || status == "Half Swept") {
    return 90;
  } 
  else {
    return 170;
  }
}
