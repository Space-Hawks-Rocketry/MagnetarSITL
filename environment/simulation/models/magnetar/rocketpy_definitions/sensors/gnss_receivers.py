from rocketpy import GnssReceiver

max_f10s_gnss = GnssReceiver(
    sampling_rate=10,
    altitude_accuracy=1.5 * 2.0, # I'll assume that altitude accuracuy is twice as bad
    position_accuracy=1.5,
    name="Max-F10S"
)

truth_gnss = GnssReceiver(
    sampling_rate=10,
    name="Max-F10S"
)