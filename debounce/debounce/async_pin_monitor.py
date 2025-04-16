import uasyncio as asyncio
import utime
from machine import Pin

class AsyncPinMonitor:  
    def __init__(self, pin, debounce_time_ms=10, active_high=False):
        self._pin = pin
        self._active_high = active_high
            
        self._stable_state = self._current_state = pin.value()
        self._state_changed = False
        
        self._debounce_ms = debounce_time_ms
        self._poll_interval_ms = 5
        self._last_state_change_ms = self._state_stable_since_ms = utime.ticks_ms()
        self._prev_state_duration_ms = 0
        
        self._monitor_task = None
        
        self._pressed_event = asyncio.Event()
        self._released_event = asyncio.Event()
    
    #-------------------------------------------------
    # Public methods
    
    def start(self, poll_interval_ms=5):
        if self._monitor_task is None:
            self._poll_interval_ms = poll_interval_ms
            self._monitor_task = asyncio.create_task(self._monitor_pin())
            
    def stop(self):
        if self._monitor_task:
            self._monitor_task.cancel()
            self._monitor_task = None
    
    async def wait_for_press(self):
        self._pressed_event.clear()
        await self._pressed_event.wait()
        
    async def wait_for_release(self):
        self._released_event.clear()
        await self._released_event.wait()
    
    #-------------------------------------------------
    # Public properties
    
    @property
    def value(self):
        return self._stable_state
    
    @property
    def debounce_time_ms(self):
        return self._debounce_ms
        
    @debounce_time_ms.setter
    def debounce_time_ms(self, new_time_ms):
        self._debounce_ms = new_time_ms
        
    @property
    def last_press_duration_s(self):
        return self._prev_state_duration_ms / 1000.0
        
    @property
    def current_press_duration_s(self):
        return utime.ticks_diff(utime.ticks_ms(), self._last_state_change_ms) / 1000.0
        
    #-------------------------------------------------
    # Private methods
    
    
    async def _monitor_pin(self):
        while True:
            pin_state = self._pin.value()
            current_time_ms = utime.ticks_ms()
            
            self._state_changed = False
            
            if pin_state != self._current_state:
                self._state_stable_since_ms = current_time_ms
                self._current_state = pin_state
            elif (self._current_state != self._stable_state and 
                  utime.ticks_diff(current_time_ms, self._state_stable_since_ms) >= self._debounce_ms):
                self._stable_state = self._current_state
                self._state_changed = True
                
                self._prev_state_duration_ms = utime.ticks_diff(current_time_ms, self._last_state_change_ms)
                self._last_state_change_ms = current_time_ms
                
                is_pressed = self._stable_state if self._active_high else not self._stable_state
                
                if is_pressed:
                    self._pressed_event.set()
                else:
                    self._released_event.set()
            
            await asyncio.sleep_ms(self._poll_interval_ms)


if __name__ == "__main__":
    button_pin = Pin(0, Pin.IN, Pin.PULL_UP)
    
    async def test_monitor():
        monitor = AsyncPinMonitor(button_pin, active_high=False)
        monitor.start()
        
        print("Press the button...")
        await monitor.wait_for_press()
        print("Button pressed!")
        
        await monitor.wait_for_release()
        print(f"Button released after {monitor.last_press_duration_s:.2f} seconds")
        
        monitor.stop()
    
    asyncio.run(test_monitor())

