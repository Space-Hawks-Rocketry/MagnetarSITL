class SITLHandle:
    '''A handle for the SITL state to be controlled by user-defined functions.'''
    
    def __init__(self, stop_delegate, t0=0, dt=0):
        self._stop_delegate = stop_delegate
        self.t = t0
        self.dt = dt
        
        self._scheduled_delegates = []
      
    def stop(self):
        '''Call this to stop the simulation.'''
        self._stop_delegate()

    def scheduleAtTime(self, t, delegate):
        '''Schedule a delegate (function) to happen at the provided simulation time'''
        time_ramaining = t - self.t
        if time_ramaining < 0:
            return
        self._scheduled_delegates.append((time_ramaining, delegate))

    def _update(self, t, dt):
        '''Update the handle. To be used by SITL_main only.'''
        self.t = t
        self.dt = dt
        ## Count down timer on scheduled delegates
        self._scheduled_delegates = [(sd[0] - dt, sd[1]) for sd in self._scheduled_delegates]
        ## Execute delegates
        self.__executeSchedule()

    def __executeSchedule(self):
        '''Execute any scheduled delegates that need to be executed.'''
        # Execute delegates that are at or past their time
        [sd[1]() for sd in self._scheduled_delegates if sd[0] <= 0]
        # Remove old delegates
        self._scheduled_delegates = [sd for sd in self._scheduled_delegates if sd[0] > 0]