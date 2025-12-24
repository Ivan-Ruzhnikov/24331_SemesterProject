// Управление шаговым двигателем NEMA17 с драйвером A4988

// Константы подключения
const int STEP_PIN = 3;
const int DIR_PIN = 2;
const int ENABLE_PIN = 4;

// Параметры двигателя и механики
const int STEPS_PER_REV = 3200;  // Шагов на оборот для NEMA17
const float SCREW_PITCH = 2;  // Шаг резьбы шпильки в мм
const float MM_PER_STEP = SCREW_PITCH / STEPS_PER_REV;
const long MKS_IN_MIN = 60000000;  //Микросекунд в минут
const int speedRPM = 60;           // Скорость вращения (RPM)
const long stepsPerMinute = (speedRPM * STEPS_PER_REV);
const int delayBetweenSteps = (MKS_IN_MIN  / stepsPerMinute) / 2;

void setup() {
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);
  digitalWrite(ENABLE_PIN, LOW);
  digitalWrite(8, HIGH);
  digitalWrite(9, HIGH);
  digitalWrite(10, HIGH);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() >0) {
    float distanceMM = Serial.parseFloat();
    bool forward = (distanceMM > 0);
    digitalWrite(DIR_PIN, forward ? HIGH : LOW);
    long steps = abs(round(distanceMM / MM_PER_STEP));
    for (long i = 0; i < steps; i++) {
      digitalWrite(STEP_PIN, HIGH);
      delayMicroseconds(delayBetweenSteps);
      digitalWrite(STEP_PIN, LOW);
      delayMicroseconds(delayBetweenSteps);
    }
}
