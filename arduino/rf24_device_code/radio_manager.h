#pragma once

#include <SPI.h>
#include "RF24.h"
#include "printf.h"

class RadioManager
{
  public:
    RadioManager()
    {
      _data_buffer[_data_buffer_size + 1] = '\0';
    }

    void initialize(RF24 *radio, const uint64_t, const uint64_t);
    void terminate();

    int transfer(const char* data, const int howmany);
    int receive(const int howmany, const int timeout);
    char* get_databuffer();

    void print_details();

  private:
    RF24 *_radio;
    uint64_t _pipe_a;
    uint64_t _pipe_b;
    char _data_buffer[32];
    const int _data_buffer_size = 30;
};

void RadioManager::initialize(RF24 *radio, const uint64_t pipe_read = 0xC2C2C2C2C2LL, const uint64_t pipe_write = 0xE7E7E7E7E7LL)
{
  _radio = radio;
  _pipe_a = pipe_read;
  _pipe_b = pipe_write;

  _radio->begin();
  _radio->setChannel(1);
  _radio->setPALevel(RF24_PA_MAX);
  _radio->setDataRate(RF24_1MBPS);
  _radio->setAutoAck(1);
  _radio->setRetries(2, 15);
  _radio->setCRCLength(RF24_CRC_8);
  
  _radio->powerUp();
}

void RadioManager::terminate()
{
  _radio->stopListening();
  _radio->powerDown();
}

void RadioManager::print_details()
{
  _radio->printDetails();
}

int RadioManager::transfer(const char* data, const int howmany)
{
  _radio->openWritingPipe(_pipe_b);
  _radio->openReadingPipe(1, _pipe_a);
  _radio->stopListening();

  int err_code = 0;
  int counter = constrain(howmany, 0, _data_buffer_size);
  unsigned long start_time = millis();

  if (!_radio->writeFast(data, counter))
  {
    err_code = -1;
  }

  _radio->txStandBy();
  _radio->stopListening();

  return err_code;
}

int RadioManager::receive(const int howmany, const int timeout)
{
  _radio->openWritingPipe(_pipe_a);
  _radio->openReadingPipe(1, _pipe_b);
  _radio->startListening();

  int err_code = 0;
  int counter = constrain(howmany, 0, _data_buffer_size);
  unsigned long start_time = millis();

  while (1)
  {
    if (millis() - start_time >= timeout)
    {
      err_code = -1;
      break;
    }

    if (_radio->available())
    {
      _radio->read(&_data_buffer, counter);
      break;
    }
  }

  _data_buffer[counter+1] = '\0';
  _radio->stopListening();

  return err_code;
}

char* RadioManager::get_databuffer()
{
  return _data_buffer;
}


