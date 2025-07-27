import brightway2 as bw
from bw2io import BW2Package
import time

# time tracking
start_time = time.time()

bw.projects.set_current('test_project')
bw.bw2setup() 

#################

start_bw = time.time()

path_materials_db_bw = "C://Users//hoel_m0//Downloads//test_materials_bw.bw2package"

BW2Package.import_file("C://Users//hoel_m0//Downloads//test_materials_bw.bw2package")

end_bw = time.time()
duration_bw = end_bw - start_bw

materials_db_bw = bw.Database("materials")

random_act_bw = materials_db_bw.random()

#################

start_xl = time.time()

# Get the path of the database.
path_materials_db_xl = "C://Users//hoel_m0//Downloads//test_materials_xl.xlsx"

materials_lca_data = bw.ExcelImporter(path_materials_db_xl)

# Apply some strategies.
materials_lca_data.apply_strategies()

# The materials database is now matched to the ecoinvent database
# to use it as a background database.
materials_lca_data.match_database("ecoinvent_3.9.1_cutoff", \
                                    fields=('name', 'unit', 'location', 'reference product'))

# In case of unlinked exchanges, they will be stored in an excel-file.
materials_lca_data.write_excel()

# The statistics() function gives an overview of the all exchanges.
materials_lca_data.statistics()

# Write all changes into the database.
materials_lca_data.write_database()

end_xl = time.time()
duration_xl = end_xl - start_xl

materials_db_xl = bw.Database("materials")

random_act_xl = materials_db_xl.random()


lca = bw.LCA({random_act_xl: 1}, method=('IPCC 2013','climate change','global warming potential (GWP100)'))

# perform the LCA
lca.lci()
lca.lcia()
    
print(lca.score)

################


# time tracking    
end_time = time.time()

duration = end_time - start_time
duration_minutes = duration // 60
duration_seconds = duration % 60

print("Time elapsed: {:.2f} seconds = {:.0f}:{:02} minutes".format(duration, duration_minutes, int(duration_seconds)))
print("Time elapsed for bw2: {:.2f} seconds".format(duration_bw))
print("Time elapsed for xl: {:.2f} seconds".format(duration_xl))