import math

from vsn.common.VSNUtility import GainSampletimeTuple


class VSNActivityController:
    def __init__(self, parameters_below_threshold, parameters_above_threshold, activation_level_threshold):
        self.__parameters_below_threshold = GainSampletimeTuple(parameters_below_threshold['gain'],
                                                                parameters_below_threshold['sample_time'])
        self.__parameters_above_threshold = GainSampletimeTuple(parameters_above_threshold['gain'],
                                                                parameters_above_threshold['sample_time'])
        self.__activation_level_threshold = activation_level_threshold

        self.__percentage_of_active_pixels = 0.0
        self.__activation_level = 0.0  # default starting activation level
        self.__activation_level_d = 0.0
        self.__parameters = self.__parameters_below_threshold  # sample time and gain at startup
        self.__activation_neighbours = 0.0  # weighted activity of neighbouring nodes

    # lowpass filter function modelled after a 1st order inertial object transformed using delta minus method
    def __lowpass(self, prev_state, input_data, gain):
        time_constant = 0.7
        output = \
            (gain / time_constant) * input_data + \
            prev_state * pow(math.e, -1.0 * (self.__parameters.sample_time / time_constant))
        return output

    def set_params(self,
                   activation_neighbours=None,
                   activation_level_threshold=None,
                   parameters_below_threshold=None,
                   parameters_above_threshold=None):
        if activation_neighbours is not None:
            self.__activation_neighbours = activation_neighbours
        if activation_level_threshold is not None:
            self.__activation_level_threshold = activation_level_threshold
        if parameters_below_threshold is not None:
            self.__parameters_below_threshold = parameters_below_threshold
        if parameters_above_threshold is not None:
            self.__parameters_above_threshold = parameters_above_threshold

    def get_sample_time(self):
        return self.__parameters.sample_time

    def get_percentage_of_active_pixels(self):
        return self.__percentage_of_active_pixels

    def get_activation_level(self):
        return self.__activation_level

    def is_activation_below_threshold(self):
        result = False
        if self.__activation_level < self.__activation_level_threshold:
            result = True
        return result

    def update_sensor_state_based_on_captured_image(self, percentage_of_active_pixels):
        # store the incoming data
        self.__percentage_of_active_pixels = percentage_of_active_pixels
        # compute the sensor state based on captured images
        activation_level_updated_d = self.__lowpass(
            self.__activation_level_d,
            percentage_of_active_pixels + self.__activation_neighbours,
            self.__parameters.gain
        )
        self.__activation_level_d = activation_level_updated_d

        activation_level_updated = self.__lowpass(
            self.__activation_level,
            self.__activation_level_d,
            1.0
        )
        # self.__activation_level = activation_level_updated + self.__activation_neighbours
        self.__activation_level = activation_level_updated

        # update sampling time and gain based on current activity level
        if self.__activation_level < self.__activation_level_threshold:
            self.__parameters = self.__parameters_below_threshold
        else:
            self.__parameters = self.__parameters_above_threshold

    def get_state_as_string(self):
        return 'Params: \r\n' + \
               '% of active pixels: ' + \
               str(self.__percentage_of_active_pixels) + \
               ', activation level: ' + \
               str(self.__activation_level) + \
               ', gain: ' + \
               str(self.__parameters.gain) + \
               ', sample time: ' + \
               str(self.__parameters.sample_time)
