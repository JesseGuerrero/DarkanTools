from DarkanTools1.tracker_backend import xp_tracker_backend as be
import matplotlib.pyplot as plt


if __name__ == "__main__":
    test = be.get_file_stats("jawarrior1", "Attack")

    # String dates
    x_axis = ["06-08", "06-09", "06-10"]

    # Actual values
    y_axis = [1, 2, 3]

    plt.plot(x_axis, y_axis)

    plt.show()

    # Assign annotation

    for each in test:
        each


    # plot
