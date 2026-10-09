import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Truth data from RocketPy
truth = pd.read_csv("truth_log.csv")

# Estimator output from flight computer
est = pd.read_csv(
    "altitude_log.csv",
    names=["time", "pressure", "height"]
)

# Convert truth altitude to AGL
truth["altitude_agl"] = (
    truth["altitude"]
    - truth["altitude"].iloc[0]
)

# Interpolate truth onto estimator timestamps
truth_interp = np.interp(
    est["time"],
    truth["time"],
    truth["altitude_agl"]
)

# Compute error
error = est["height"] - truth_interp

# Metrics
rmse = np.sqrt(np.mean(error**2))
max_error = np.max(np.abs(error))

# Apogee
truth_apogee_idx = truth_interp.argmax()
est_apogee_idx = est["height"].argmax()

truth_apogee_time = est["time"].iloc[truth_apogee_idx]
est_apogee_time = est["time"].iloc[est_apogee_idx]

print(f"RMSE = {rmse:.3f} m")
print(f"Max Error = {max_error:.3f} m")
print(f"Truth Apogee Time = {truth_apogee_time:.3f} m")
print(f"Estimated Apogee Time = {est_apogee_time:.3f} m")
print(f"Apogee Timing Error = {est_apogee_time - truth_apogee_time:.3f} s")

# Plot altitude comparison
fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(10, 8),
    sharex=True
)

ax1.plot(
    est["time"],
    truth_interp,
    label="RocketPy Truth",
    linewidth=3
)

ax1.plot(
    est["time"],
    est["height"],
    label="Barometric Estimate",
    linewidth=2
)

ax1.set_ylabel("Altitude (m)")
ax1.set_title("Truth vs Barometric Altitude")
ax1.legend()
ax1.grid(True)

# Plot error
ax2.plot(
    est["time"],
    error,
    linewidth=2
)

ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Error (m)")
ax2.set_title("Altitude Estimation Error")
ax2.grid(True)

plt.tight_layout()

# fig = plt.plot(truth_interp, error)
plt.show()

