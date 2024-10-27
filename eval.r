# Load necessary library
#library(readr)

# Load necessary library for plotting
library(ggplot2)
library(ggpubr)

# List of files to process
files <- list("RX.csv", "RG.csv", "RB.csv", "TH.csv")
titles <- lapply(files, function(file) {
    prefix <- tools::file_path_sans_ext(basename(file))
    paste("Hub", prefix, "uncompensated/uncalibrated angular velocity vs temperature")
})
# Create a PDF file to save all plots
pdf("hubs.pdf")

# Initialize variables to store the combined x and y ranges
x_min <- Inf
y_min <- Inf
y_max <- -Inf

# Iterate over the files to find the combined x and y ranges
for (file in files) {
    data <- read.csv(file)
    x_min <- min(x_min, min(data$temp, na.rm = TRUE))
    y_min <- min(y_min, min(data$xaxis, data$yaxis, data$zaxis, na.rm = TRUE))
    y_max <- max(y_max, max(data$xaxis, data$yaxis, data$zaxis, na.rm = TRUE))
}

# Iterate over the files
for (i in 1:length(files)) {
    # Read the CSV file
    data <- read.csv(files[[i]])

    # Create the plot
    plot <- ggscatter(data, x = "temp", y = "xaxis", color = "blue", add = "reg.line", conf.int = FALSE) +
        stat_regline_equation(aes(label = ..eq.label..), label.x = x_min, label.y = y_max, color = "blue") +
        geom_text(aes(x = mean(data$temp), y = mean(data$xaxis), label = "X-axis"), hjust = 0, vjust = 3, color = "blue") +
        geom_point(aes(x = temp, y = yaxis), color = "brown") +
        geom_smooth(aes(x = temp, y = yaxis), method = "lm", se = FALSE, color="brown") +
        stat_regline_equation(aes(x = temp, y = yaxis, label = ..eq.label..), label.x = x_min, label.y = y_max * 0.9, color = "brown") +
        geom_text(aes(x = mean(data$temp), y = mean(data$yaxis), label = "Y-axis"), hjust = 0, vjust = 3, color = "brown") +
        geom_point(aes(x = temp, y = zaxis), color = "darkgreen") +
        geom_smooth(aes(x = temp, y = zaxis), method = "lm", se = FALSE, color="darkgreen") +
        stat_regline_equation(aes(x = temp, y = zaxis, label = ..eq.label..), label.x = x_min, label.y = y_max * 0.8, color = "darkgreen") +
        geom_text(aes(x = mean(data$temp), y = mean(data$zaxis), label = "Z-axis"), hjust = 0, vjust = 3, color = "darkgreen") +
        ggtitle(titles[[i]]) +
        xlab("[C]") +
        ylab("[deg/s]") +
        ylim(y_min, y_max)
    # Print the plot to the PDF file
    print(plot)
}

# Close the PDF file
dev.off()
