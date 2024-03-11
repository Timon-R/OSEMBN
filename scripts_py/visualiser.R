#Works in tandem with the python script to create a chord diagram.
#@author: Timon Renzelmann

library(tidyverse)
library(viridis)
library(patchwork)
library(hrbrthemes)
library(circlize)
library(chorddiag)  #devtools::install_github("mattflor/chorddiag") needs to be installed

create_chord <- function(dataframe, title, r_index, r_columns){
  svg(filename = paste0("visualisations/chord_diagram_", title, ".svg"))
  rownames(dataframe) <- r_index
  colnames(dataframe) <- r_columns
  # I need a long format
  data_long <- dataframe %>%
  rownames_to_column %>%
  gather(key = "key", value = "value", -rowname)
# parameters
  circos.clear()
  circos.par(
    start.degree = 90,
    gap.degree = 4,
    track.margin = c(-0.1, 0.1),
    points.overflow.warning = FALSE
  )
  par(mar = rep(0, 4))
  # color palette
  sector_names <- unique(data_long$key)
  mycolor <- viridis(
    length(sector_names), alpha = 1, begin = 0, end = 1, option = "D"
  )
  names(mycolor) <- sector_names
  # Base plot
  # Extract the range of values from the dataframe
  chordDiagram(
    x = data_long,
    grid.col = mycolor,
    transparency = 0.25,
    directional = 1,
    direction.type = c("arrows", "diffHeight"),
    diffHeight  = -0.04,
    annotationTrack = "grid",
    annotationTrackHeight = c(0.05, 0.1),
    link.arr.type = "big.arrow",
    link.sort = TRUE,
    link.largest.ontop = TRUE
  )
  # Add text and axis
  # Add text and axis
  circos.trackPlotRegion(
    track.index = 1,
    bg.border = NA,
    panel.fun = function(x, y) {
      xlim <- get.cell.meta.data("xlim")
      sector_index <- get.cell.meta.data("sector.index")
      circos.text(
        x = mean(xlim),
        y = 4,
        labels = sector_index,
        facing = "bending",
        cex = 1.3
      )
      #Create sequence of tick marks that covers the entire range of the sector
      tick_marks <- seq(from = round(xlim[1]), to = round(xlim[2]), by = 5)
      # Create a sequence of labels that covers the range of the data
      labels <- seq(from = round(xlim[1]), to = round(xlim[2]), by = 25)
      # Add graduation on axis
      circos.axis(
        h = "top",
        major.at = tick_marks,  # Use tick_marks for major tick marks
        major.tick.length = 0.5,
        minor.ticks = 0,
        labels = NULL,
        labels.niceFacing = FALSE
      )
      # Add labels manually
      for (label in labels) {
        circos.text(
          x = label,
          y = 2,
          labels = as.character(label),
          facing = "bending",
          cex = 0.9
        )
      }
    }
  )
  dev.off()
}