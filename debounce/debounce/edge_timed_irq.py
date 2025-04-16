from utime import ticks_us, ticks_diff
import asyncio

class EdgeTimedIRQ:
    def __init__(self, pin, debounce_ms=200, 
                 active_low=True, trigger_edge=None):
        self._prior_interrupt_us = ticks_us()
        self._debounce_ms = debounce_ms
        self._active_low = active_low
        self._pin = pin
        self._debounced_state = False
        self._event_timestamp = 0
        self._state_flag = asyncio.ThreadSafeFlag()
        
        if trigger_edge is None:
            self._edge_type = self._pin.IRQ_FALLING if active_low else self._pin.IRQ_RISING
        else:
            self._edge_type = trigger_edge
    
    #-------------------------------------------------
    # Public methods
    
    def start(self):
        self._pin.irq(trigger=self._edge_type, handler=self._button_irq)
    
    def stop(self):
        self._pin.irq(trigger=0, handler=None)
    
    def get_state(self):
        return self._debounced_state
    
    async def wait_for_event(self):
        await self._state_flag.wait()
        return self._event_timestamp
    
    #-------------------------------------------------
    # Private methods
    
    def _button_irq(self, _):
        now = ticks_us()
        diff = ticks_diff(now, self._prior_interrupt_us) // 1000
        
        if diff > self._debounce_ms:
            if self._edge_type == self._pin.IRQ_FALLING:
                self._debounced_state = True if self._active_low else False
            else:
                self._debounced_state = True if not self._active_low else False
            
            self._event_timestamp = now
            self._state_flag.set()
        
        self._prior_interrupt_us = now


if __name__ == "__main__":
    import machine
    from time import sleep_ms
    
    test_pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
    button = EdgeTimedIRQ(test_pin)
    button.start()
    
    async def test_button():
        print("Waiting for button press...")
        while True:
            timestamp = await button.wait_for_event()
            print(f"Button pressed at {timestamp} microseconds")
            print(f"Button state: {button.get_state()}")
            await asyncio.sleep(0.1)
    
    asyncio.run(test_button())
