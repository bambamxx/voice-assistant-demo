from seaplane.apps import App

# import DAGs
from DAG_seari import seari_dag

# create the seari app
app = App("sea-ri")

# create new instance of the siri dag
output = seari_dag(app, "sea-ri-d", app.input())

# send output out of app
app.respond(output)

# run the app
app.run()
