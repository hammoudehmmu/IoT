configuration NodeAppC { }
implementation
{
    components NodeC, MainC, ActiveMessageC, LedsC,
        new TimerMilliC(),
        new PhotoC() as PhotoSensor,
        new TempC() as TempSensor,
        new AMSenderC(AM_NODEREAD),
        new AMReceiverC(AM_NODEREAD);

    NodeC.Boot -> MainC;
    NodeC.RadioControl -> ActiveMessageC;
    NodeC.AMSend -> AMSenderC;
    NodeC.Receive -> AMReceiverC;
    NodeC.Timer -> TimerMilliC;
    NodeC.PhotoRead -> PhotoSensor;
    NodeC.TempRead -> TempSensor;
    NodeC.Leds -> LedsC;
}
