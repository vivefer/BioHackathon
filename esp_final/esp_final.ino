#include <WiFi.h>
#include <HTTPClient.h>
#include <math.h>

// Wi-Fi credentials
const char* ssid = "HARDISH";
const char* password = "987654322";

// Flask server details
const char* serverIP = "192.168.16.125";  // Replace with the Flask server's IP address
const int serverPort = 5000;             // Flask server port
const char* endpoint = "/api/person";    // Flask endpoint

// Define pin connections for soil moisture sensor
const int moisturePin = 34;  // Analog pin connected to soil moisture sensor

// Variables to store sensor values
int moistureValue = 0;        // Analog value from the sensor
float voltage = 0.0;          // Calculated voltage
float conductivity = 0.00;     // Approximate electrical conductivity (in mS/cm)
float abeta_concentration = 0.0;

// Calibration constants
const float VCC = 5.0;        // Voltage of the Arduino (5V)
const float maxEC = 5.0;      // Maximum electrical conductivity (calibrated, in mS/cm)

void setup() {
  Serial.begin(115200);   // Initialize serial communication
  delay(10);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  int maxAttempts = 20;  // Number of attempts before timing out
  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED && attempts < maxAttempts) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected to WiFi");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect to WiFi.");
    while (true) {
      delay(1000);  // Halt execution to prevent unnecessary operations
    }
  }
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Read the moisture sensor value
    moistureValue = analogRead(moisturePin);
    Serial.print("Moisture Value: ");
    Serial.println(moistureValue);  // Debugging sensor value

    // Convert analog value to voltage
    voltage = (moistureValue / 1023.0) * VCC;
    Serial.print("Voltage: ");
    Serial.println(voltage);  // Debugging voltage

    
    // Map the moisture value to a normalized range (0 to 1)
  //  float normalizedMoisture = map(moistureValue, wetValue, dryValue, 100, 0) / 100.0;
    // normalizedMoisture = constrain(normalizedMoisture, 0.0, 1.0);  // Ensure within bounds
   // Serial.print("Normalized Moisture: ");
   // Serial.println(normalizedMoisture);  // Debugging normalized moisture

    // Calculate conductivity (in microsiemens per cm)
    conductivity = moistureValue * maxEC;  // in microsiemens per cm
    Serial.print("Conductivity: ");
    Serial.println(conductivity);  // Debugging conductivity

    // Calculate abeta concentration (calibration can be adjusted)
    abeta_concentration = (10000 - conductivity) / 15;
    Serial.print("Abeta Concentration: ");
    Serial.println(fabs(abeta_concentration));  // Debugging abeta concentration

    // Construct JSON data for the POST request
    String jsonData = String("{\"name\":\"ESP32 Soil Sensor\",")
                      + "\"conductivity\":" + String(conductivity, 2) + ","
                      + "\"abeta_concentration\":" + String(fabs(abeta_concentration), 2) + "}";

    // Construct URL for Flask server
    String url = String("http://") + serverIP + ":" + String(serverPort) + endpoint;
    http.begin(url);  // Initialize HTTP connection

    // Add headers
    http.addHeader("Content-Type", "application/json");
    Serial.println("Sending data to Flask server...");

    // Send POST request with the sensor data
    int httpResponseCode = http.POST(jsonData);

    // Check response
    if (httpResponseCode > 0) {
      Serial.print("HTTP Response Code: ");
      Serial.println(httpResponseCode);
      String response = http.getString();
      Serial.print("Response: ");
      Serial.println(response);
    } else {
      Serial.print("Error in sending POST: ");
      Serial.println(http.errorToString(httpResponseCode).c_str());
    }

    http.end();  // Close HTTP connection
  } else {
    Serial.println("WiFi not connected!");
  }

  delay(2000);  // Send data every 2 seconds
}