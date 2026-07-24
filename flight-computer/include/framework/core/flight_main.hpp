#include <nlohmann/json.hpp>
using json = nlohmann::json;

/// @brief The result of a single control step, including how much time it took (or would've taken irl) and the control actions to apply (such as deploying a parachute).
typedef struct ControlStepTag {
    /// @brief Arbitary json object representing control commands to send to the environment sim.
    json control_msg;
    /// @brief The time that this function call took to execute. For irl accuracy, this should correspond to the predicted amount of time your actual flight computer would take.
    double execution_time;
} ControlStep;

ControlStep setup(json sensor_data);
ControlStep loop(json sensor_data);