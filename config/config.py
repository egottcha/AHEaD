'''
Created on 2013.09.07.
'''

class Config():
    DEVELOPER_MODE_ON = True
    
class SensorConfig:
    TIME_BETWEEN_TWO_MEASUREMENT_IN_SEC = 4
    TIME_FOR_ACTION_CHECK = 0.05
    TIME_MOTOR_SPEED_SLOW = 0.004
    TIME_MOTOR_SPEED_FAST = 0.003
    DISTANCE_TRIGGER_STANDBY_START = 40
    DISTANCE_TRIGGER_STANDBY_END = 50
    DISTANCE_TRIGGER_ACTION_START = 10
    DISTANCE_TRIGGER_ACTION_END = 20

    SENSOR_MODEL_TEMP = 22
    GPIO_TEMP_HUM = 7
    GPIO_DISTANCE_ECHO = 24
    GPIO_DISTANCE_TRIG = 23
    GPIO_MOTION = 25
    #GPIO_MOTOR_ENABLE = 7
    GPIO_MOTOR_IN_1 = 17
    GPIO_MOTOR_IN_2 = 18
    GPIO_MOTOR_IN_3 = 27
    GPIO_MOTOR_IN_4 = 22
    GPIO_RELAY_IN_1 = 4
    GPIO_RELAY_IN_4 = 10
    
class MqttConfig:
    MQTT_SERVER_URL = "test.mosquitto.org"
    LOG_TOPIC = "ahead/node/log/#"
    TOPIC_LOG_TEMP_HUM = "ahead/node/log/temphum"
    TOPIC_LOG_LUX = "ahead/node/log/lux"
    TOPIC_LOG_DISTANCE = "ahead/node/log/distance"
    TOPIC_LOG_MOTION = "ahead/node/log/motion"
    TOPIC_LOG_MOTOR = "ahead/node/log/motor"
    TOPIC_LOG_RELAY = "ahead/node/log/relay"
    TOPIC_LOG_POWER = "ahead/node/log/power"
    
class DbConfig:
    MONGODB_URL = 'localhost'
    MONGODB_PORT = 27017
    MONGODB_DATABASE = 'ahead'
    MONGODB_SENSOR_TABLE = 'sensor'
    MONGODB_USER_TABLE = 'user'  # check if user table is in use in MongoDB
    MONGODB_NODE_LOOKUP_TABLE = 'node'
    MONGODB_USER_HABIT_TABLE = 'habit'
    MONGODB_REQUEST_TABLE = 'request'
