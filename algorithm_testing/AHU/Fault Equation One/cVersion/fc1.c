#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <stdbool.h>

// compile on Ubuntu
// $ gcc fc1.c -o fc1
// then program run with 
// $ ./fc1

// ASHRAE Guideline 36 fault detection parameters
#define VFD_SPEED_ERR_THRES 0.05
#define VFD_SPEED_MAX_THRES 0.99
#define PRESSURE_ERR_THRES 0.1

// fake data parameters
const float pressure_low = 0.5;
const float pressure_high = 1.5;
const float setpoint_low = 1.0;
const float setpoint_high = 1.4;
const float motor_speed_low = 20.5;
const float motor_speed_high = 95.5;

float generate_random_machine() {
    return ((float)rand()/(float)(RAND_MAX)) * (pressure_high - pressure_low) + pressure_low;
}

void generate_random_data(float* pressure_data_storage, float* setpoint_data_storage, float* motor_speed_data_storage) {
    while (1) {
        float pressure = generate_random_machine();
        float setpoint = ((float)rand()/(float)(RAND_MAX)) * (setpoint_high - setpoint_low) + setpoint_low;
        float motor_speed = ((float)rand()/(float)(RAND_MAX)) * (motor_speed_high - motor_speed_low) + motor_speed_low;

        *pressure_data_storage = pressure;
        *setpoint_data_storage = setpoint;
        *motor_speed_data_storage = motor_speed;

        pressure_data_storage++;
        setpoint_data_storage++;
        motor_speed_data_storage++;

        sleep(1);
    }
}

float calc_mean(float* list_data, int length) {
    float sum = 0;
    for (int i = 0; i < length; i++) {
        sum += *(list_data + i);
    }
    return sum / length;
}

int fault_check(float* pressure_data_storage, float* setpoint_data_storage, float* motor_speed_data_storage, int length) {
    // Calculate the mean values of pressure, setpoint, and motor_speed
    float pressure_mean = calc_mean(pressure_data_storage, length);
    float setpoint_mean = calc_mean(setpoint_data_storage, length);
    float motor_speed_mean = calc_mean(motor_speed_data_storage, length);

    // Check if the pressure is below the setpoint minus a threshold, and if the fan speed is above a maximum threshold minus a small error threshold
    int pressure_check = pressure_mean < (setpoint_mean - PRESSURE_ERR_THRES);
    int fan_check = motor_speed_mean >= (VFD_SPEED_MAX_THRES - VFD_SPEED_ERR_THRES);

    // if there isn't a full 5 minutes of simulated data
    if (length < 300) {
        return 0;
    } else {
        // Return 1 if both checks are true, indicating a fault has occurred, and 0 otherwise
        return pressure_check && fan_check;
    }
}

int main() {
    srand(time(NULL));

    float pressure_data_storage[300], setpoint_data_storage[300], motor_speed_data_storage[300];

    // start the data simulation in a separate thread
    pid_t pid = fork();
    if (pid == 0) {
        generate_random_data(pressure_data_storage, setpoint_data_storage, motor_speed_data_storage);
    }

    while (1) {
        // Check for faults in the generated data and print the result
        printf("FAULT DETECTION IS: %d\n", fault_check(pressure_data_storage, setpoint_data_storage, motor_speed_data_storage, 300));
        sleep(300);
    }

    return 0;
}
