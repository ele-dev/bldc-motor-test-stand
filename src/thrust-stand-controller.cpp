#include <Arduino.h>
#include "HX711.h"

const int ESC_PIN = 9; // MUST be Pin 9 (tied to Timer 1 / OC1A)
const int HX711_CLK_PIN = 3;
const int HX711_DT_PIN = 2;

const float SCALE_CALIBRATION_FACTOR = 660.0f;

HX711 scale;

float filteredThrust = 0.0f;
const float alpha = 0.15f;

const bool periodicReports = false;
const unsigned long reportInterval = 400;
unsigned long lastReportTime = 0;

// periodic throttle commands must be received faster to keep motor spinning
const bool safeThrottleControl = true;
const unsigned long throttleCmdInterval = 3000;
unsigned long lastThrottleCmd = 0;
int dutyCycleUs = 1000; // Target pulse width in microseconds

String inputBuffer = "";

// function declarations
void setupHardwarePWM();
void setESCValue(int microseconds);
void checkSerialCommands();
void processThrottle(String command);
void setup();
void loop();

void setupHardwarePWM()
{
    // Configure Pin 9 as an output
    pinMode(ESC_PIN, OUTPUT);

    // Clear Timer 1 control registers
    TCCR1A = 0;
    TCCR1B = 0;
    TCNT1 = 0;

    // Set WGM13 and WGM12 and WGM11 (Mode 14: Fast PWM with ICR1 as TOP)
    TCCR1A |= (1 << COM1A1) | (1 << WGM11);
    TCCR1B |= (1 << WGM13) | (1 << WGM12);

    // Set Prescaler to 8 (16MHz / 8 = 2MHz clock, meaning 1 tick = 0.5 microseconds)
    TCCR1B |= (1 << CS11);

    // Set the TOP value for a 400Hz frequency (2,500 microseconds period)
    // 2,500 us / 0.5 us per tick = 5,000 ticks
    ICR1 = 5000;

    // Set initial duty cycle to 1000 microseconds (1000 us / 0.5 us = 2000 ticks)
    OCR1A = 2000;
}

void setESCValue(int microseconds)
{
    // Constrain to safe ESC limits (1ms to 2ms)
    microseconds = constrain(microseconds, 1000, 2000);

    // Convert microseconds to Timer 1 ticks (multiply by 2 because 1 tick = 0.5 us)
    // At 400Hz, 1000us = 2000 ticks (40% duty cycle) and 2000us = 4000 ticks (80% duty cycle)
    OCR1A = microseconds * 2;
}

void setup()
{
    Serial.begin(115200);

    // Initialize pure hardware PWM on Pin 9
    setupHardwarePWM();

    // Wait 2 seconds for the ESC to arm at 1000us
    delay(2000);
    Serial.println("Initialized ESC via Hardware PWM.");

    Serial.println("Preparing the load cell scale ...");
    scale.begin(HX711_DT_PIN, HX711_CLK_PIN);
    scale.set_scale(SCALE_CALIBRATION_FACTOR);
    scale.tare();
    Serial.println("Initialized the scale.");
    Serial.println("Setup complete.");
}

void loop()
{

    checkSerialCommands();

    unsigned long currentMillis = millis();
    if (currentMillis - lastThrottleCmd >= throttleCmdInterval && safeThrottleControl)
    {
        if (dutyCycleUs != 1000)
        {
            // reset throttle to zero to stop motor
            dutyCycleUs = 1000;
            setESCValue(dutyCycleUs);
            Serial.println("Reset throttle to zero.");
            lastThrottleCmd = currentMillis;
        }
    }

    if (scale.is_ready())
    {
        float rawThrust = scale.get_units(1);

        // Apply EMA filter immediately to catch every single hardware sample
        filteredThrust = (alpha * rawThrust) + ((1.0f - alpha) * filteredThrust);
    }

    if (periodicReports)
    {
        currentMillis = millis();
        if (currentMillis - lastReportTime >= reportInterval)
        {
            Serial.print("Filtered Thrust: ");
            Serial.print(filteredThrust, 1);
            Serial.print(" g | Throttle: ");
            Serial.print(dutyCycleUs);
            Serial.println(" us");

            lastReportTime = currentMillis;
        }
    }
}

void checkSerialCommands()
{
    while (Serial.available() > 0)
    {
        char inChar = (char)Serial.read();

        if (inChar == '\n' || inChar == '\r')
        {
            if (inputBuffer.length() > 0)
            {
                inputBuffer.trim();
                processThrottle(inputBuffer);
                inputBuffer = "";
            }
        }
        else
        {
            if (inputBuffer.length() < 6)
            {
                inputBuffer += inChar;
            }
        }
    }
}

void processThrottle(String command)
{
    int parsedValue = command.toInt();

    if (parsedValue >= 1000 && parsedValue <= 2000)
    {
        dutyCycleUs = parsedValue;
        setESCValue(dutyCycleUs); // Updates hardware register instantly
        Serial.print(">> Throttle set to: ");
        Serial.println(dutyCycleUs);
        lastThrottleCmd = millis();
    }
    else
    {
        Serial.println(">> Error: Out of range (1000-2000).");
    }
}