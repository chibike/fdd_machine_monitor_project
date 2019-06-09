#include "radio_manager.h"

#define LEN_INT_ARRAY(A) (sizeof(A) / sizeof(int))

RF24 radio(9, 10);
RadioManager radio_manager;

const int threshold = 100;
const int sensor_analog_pin = A0;
const int status_led = 8;

const int user_id_selection_pin[] = {7, 6, 5, 4, 3, A7};

const uint64_t pipe_a = 0x0222222222LL;
const uint64_t pipe_b = 0x1222222222LL;

uint8_t user_id = 5;
uint8_t state = 0;
char* data_to_send = "{00}\n";

void setup()
{
  Serial.begin(115200);
  printf_begin();

  radio_manager.initialize(&radio, pipe_a, pipe_b);
  radio_manager.print_details();

  pinMode(status_led, OUTPUT);
  for (int i=0; i<LEN_INT_ARRAY(user_id_selection_pin); i++)
  {
    pinMode(user_id_selection_pin[i], OUTPUT);
  }
}

void loop()
{
  static long last_loop_time = millis();
  int sensor_level = analogRead(sensor_analog_pin);

  state = (sensor_level > threshold) ? 1 : 0;
  user_id = 0;

  for (int i=0; i<LEN_INT_ARRAY(user_id_selection_pin); i++)
  {
    if (digitalRead(user_id_selection_pin[i]))
    {
      user_id = i+1;
      break;
    }
  }

  data_to_send[1] = (char) state+48;
  data_to_send[2] = (char) user_id+48;

  if (millis() - last_loop_time >= 1000)
  {
    state = (state == 0) ? 1:0;
    last_loop_time = millis();

    Serial.print("state: ");
    Serial.println(state);
    Serial.print("data_to_send: ");
    Serial.println(data_to_send);

    if (state)
    {
      digitalWrite(status_led, !digitalRead(status_led));
    }
    else
    {
      digitalWrite(status_led, true);
    }
  }

  radio_manager.transfer(data_to_send, 4);
  delay(100);
}

