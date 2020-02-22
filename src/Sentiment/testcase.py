import guba 
import json
db,to_tscode,to_name = guba.init_utils()
with guba.DataBase() as dbo:
    latest=[x[0] for x in dbo._exe("select * from latest")]
with open("testcase","w") as f:
    json.dump(latest,f)