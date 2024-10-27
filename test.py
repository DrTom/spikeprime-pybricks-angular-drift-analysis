# WARNING: this script is for testing purposes and requires patches not merged
# into the main pybricks-micropython repository; at the time of writing this
# code will not run with official neither nightly builds of pybricks-micropython

from pybricks import version
from pybricks.hubs import InventorHub
from pybricks.parameters import Icon, Port
from pybricks.pupdevices import Motor
from pybricks.tools import run_task, wait, StopWatch, multitask, vector

REPORT_INTERVAL_SECS = 15
HEAT_UP_STEP_DURATION_SECS = 15
IMU_MAX_TEMP = 65

curr_power = 0
hub = InventorHub()

print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
print("Testing")
print("Hub: ", hub.system.name())
print("Pybricks version:", version)
print("Pybricks IMU settings:", hub.imu.settings())
print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")


# two large lego angular motors
motor1 = Motor(Port.A)
motor2 = Motor(Port.E)
motors = [motor1, motor2]

stop_watch = StopWatch()


async def wait_until_next_interval_starts(interval_dur_secs):
    await wait((interval_dur_secs - (stop_watch.time()/1000 % interval_dur_secs)) * 1000)


async def output_print_loop():
    print(
        "Time[secs], pwr, Temperature[C], angular_velocity[deg/sec]")
    while True:
        await wait_until_next_interval_starts(REPORT_INTERVAL_SECS)
        time = stop_watch.time()
        temperature = hub.imu.temperature()
        COUNT = 1000
        angular_velocity = vector(0, 0, 0)
        for _ in range(COUNT):
            angular_velocity += hub.imu.angular_velocity(calibrated=False)
        angular_velocity /= COUNT
        x, y, z = angular_velocity

        print("{:4d}, {:4d}, {:3.1f}, {:5.2f}, {:5.2f}, {:5.2f}".format(
            int(stop_watch.time() / 1000), curr_power, temperature, x, y, z))


async def heat_up_hub():
    print("### Heating up the hub ###")

    async def set_power():
        hub.display.icon(Icon.FULL / 100 * curr_power)
        for motor in motors:
            motor.dc(curr_power)
        await wait(1)

    async def power_increase():
        global curr_power
        if curr_power < 100:
            curr_power += 1
        await set_power()
        await wait(1)

    async def power_off():
        global curr_power
        curr_power = 0
        await set_power()
        await wait(1)

    async def heat_up():
        prev_temperature = round(hub.imu.temperature(), 1)
        while hub.imu.temperature() < IMU_MAX_TEMP:
            await wait_until_next_interval_starts(HEAT_UP_STEP_DURATION_SECS)
            temperature = round(hub.imu.temperature(), 1)
            if temperature <= prev_temperature:
                await power_increase()
            prev_temperature = temperature

    await heat_up()
    await power_off()
    await wait(30 * 1000)


run_task(multitask(
    output_print_loop(),
    heat_up_hub(),
    race=True))
