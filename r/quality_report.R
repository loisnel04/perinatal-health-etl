# R data quality report for the perinatal ETL portfolio project.
# Run from the project root with: Rscript r/quality_report.R

required_packages <- c(
  "readr",
  "dplyr",
  "ggplot2"
)

installed <- rownames(installed.packages())

suppressPackageStartupMessages({
  for (pkg in required_packages) {
    if (!(pkg %in% installed)) {
      install.packages(pkg, repos = "https://cloud.r-project.org")
    }

    library(pkg, character.only = TRUE)
  }
})

records_path <- "output/perinatal_records.csv"
rejected_path <- "output/rejected_records.csv"
report_path <- "output/data_quality_report.txt"
plot_path <- "output/delivery_mode_distribution.png"

records <- read_csv(records_path, show_col_types = FALSE)
rejected <- read_csv(rejected_path, show_col_types = FALSE)

summary_lines <- c(
  "Perinatal ETL Data Quality Report",
  "==================================",
  paste("Generated at:", Sys.time()),
  paste("Valid records:", nrow(records)),
  paste("Rejected records:", nrow(rejected)),
  paste("Average birth weight:", round(mean(records$birth_weight_grams, na.rm = TRUE), 1), "grams"),
  paste("Average gestational age:", round(mean(records$gestational_age_weeks, na.rm = TRUE), 1), "weeks"),
  "",
  "Missing values per field:",
  paste(capture.output(print(colSums(is.na(records)))), collapse = "\n"),
  "",
  "Rejected record reasons:",
  if (nrow(rejected) > 0) paste(capture.output(print(rejected %>% count(error_reason))), collapse = "\n") else "None"
)

writeLines(summary_lines, report_path)

if (nrow(records) > 0) {
  p <- records %>%
    count(delivery_mode) %>%
    ggplot(aes(x = delivery_mode, y = n)) +
    geom_col() +
    labs(
      title = "Delivery mode distribution",
      x = "Delivery mode",
      y = "Number of records"
    ) +
    theme_minimal()

  ggsave(plot_path, p, width = 8, height = 5)
}

cat("Report written to", report_path, "\n")
