import xp_tracker_backend as be
import matplotlib.pyplot as plt
from datetime import date, timedelta

if __name__ == "__main__":

    #TODO: Annotate
    def xpTracker(player, stat_name, days = 7):
        x_axis = []
        y_axis = []
        stat_profile = be.get_file_stats(player, stat_name, days)

        for stat in stat_profile:
            x_element = str(stat.getDate())[-5:]
            x_axis.append(x_element)

            y_element = stat.getValue()
            y_axis.append(y_element)
        plt.plot(x_axis, y_axis)
        plt.show()

    xpTracker("garlic pork", "totalXp", 7)


