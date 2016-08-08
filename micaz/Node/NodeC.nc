#include "Timer.h"
#include "Node.h"
#include "TinyError.h"

module NodeC @safe()
{
    uses {
        interface Boot;
        interface SplitControl as RadioControl;
        interface AMSend;
        interface Receive;
        interface Timer<TMilli>;
        interface Read<uint16_t> as PhotoRead;
        interface Read<uint16_t> as TempRead;
        interface Leds;
    }
}
implementation
{
    message_t sendBuf;
    readings_t localPhoto;
    readings_t localTemp;
    uint8_t photoreading;
    uint8_t tempreading;

    void report_problem() {
        call Leds.led0On();
    }
    void report_sent() {
        call Leds.led1Toggle();
    }
    void report_received() {
        call Leds.led2Toggle();
    }

    event void Boot.booted() {
        localPhoto.ttl = 2;
        localPhoto.id = TOS_NODE_ID;
        localPhoto.type = PHOTO;
        localTemp.ttl = 2;
        localTemp.id = TOS_NODE_ID;
        localTemp.type = TEMP;
        if (call RadioControl.start() != SUCCESS)
            report_problem();
    }

    void startTimer() {
        call Timer.startPeriodic(DEFAULT_INTERVAL);
        photoreading = 0;
        tempreading = 0;
    }

    event void RadioControl.startDone(error_t error) {
        startTimer();
    }

    event void RadioControl.stopDone(error_t error) {
    }

    bool send(readings_t* payload) {
        uint8_t tries;
        tries = 5;
        if (sizeof *payload <= call AMSend.maxPayloadLength()) {
            memcpy(call AMSend.getPayload(&sendBuf, sizeof(*payload)), payload, sizeof *payload);
            while (tries-- > 0) {
                switch (call AMSend.send(AM_BROADCAST_ADDR, &sendBuf, sizeof *payload)) {
                    case SUCCESS:
                        return TRUE;
                    case FAIL:
                        report_problem();
                        return FALSE;
                }
            }
        }
        return FALSE;
    }

    event message_t* Receive.receive(message_t* msg, void* payload, uint8_t len) {
        readings_t* load = (readings_t*) payload;
        if (load->id == TOS_NODE_ID || load->ttl-- == 0)
            return msg;
        send(load);
        return msg;
    }

    event void Timer.fired() {
        if (photoreading >= NREADINGS) {
            if (send(&localPhoto)) {
                photoreading = 0;
                localPhoto.count++;
            }
        }
        if (tempreading >= NREADINGS) {
            if (send(&localTemp)) {
                tempreading = 0;
                localTemp.count++;
            }
        }
        if (call PhotoRead.read() != SUCCESS)
            report_problem();
        if (call TempRead.read() != SUCCESS)
            report_problem();
    }

    event void AMSend.sendDone(message_t* msg, error_t error) {
        if (error == SUCCESS)
            report_sent();
        else
            report_problem();
    }

    event void TempRead.readDone(error_t result, uint16_t data) {
        if (result != SUCCESS) {
            data = 0xffff;
            report_problem();
        }
        if (tempreading < NREADINGS) 
            localTemp.readings[tempreading++] = data;
    }

    event void PhotoRead.readDone(error_t result, uint16_t data) {
        if (result != SUCCESS) {
            data = 0xffff;
            report_problem();
        }
        if (photoreading < NREADINGS) 
            localPhoto.readings[photoreading++] = data;
    }
}
