"""
This module runs every data processing module after the APIs have been accessed.

Author: Steve Bischoff
"""
import dump_columns
import create_raw_dataframe
import create_standardized_dataframe
import create_total_pca_dataframe
import get_max_distance
import fit_knns

dump_columns.main()
create_raw_dataframe.main()
create_standardized_dataframe.main()
create_total_pca_dataframe.main()
get_max_distance.main()
fit_knns.main()
