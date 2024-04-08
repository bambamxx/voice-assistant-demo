# import tasks
from TASK_RAG_weather import rag_weather
from TASK_category_post_processing import category_post_processing
from TASK_RAG_stocks import rag_stocks
from TASK_dummy import dummy
from TASK_brewery import brewery as brewery_task


def rag_dag(app, name, input):
    """
    This function creates a DAG (Directed Acyclic Graph) to retrieve relevant RAG (retrieval augmented generation) information for the Seari chatbot
    based on the associated categories extracted from the input message.

    Args:
        app (Application): The application instance.
        name (str): The name of the DAG.
        input (Message): The input message.

    Returns:
        dag: The created DAG instance.

    DAG Response:
        output (Message): The output message containing the RAG information.
    """

    # create a new dag instance
    dag = app.dag(name)

    # category post processing to set the correct routing parameter
    category = dag.task(category_post_processing, [input], instance_name="cat-ppf")

    # run through RAG DAG to retrieve relevant information
    weather = category.if_(lambda c: c.category == "weather")
    stocks = category.if_(lambda c: c.category == "stocks")
    brewery = category.if_(lambda c: c.category == "breweries")
    other_out = category.if_(lambda c: c.category == "other")

    # ADD MORE RAG TASKS HERE TO EXTEND FUNCTIONALITY

    # retrieve RAG based on the category
    weather_out = dag.task(rag_weather, [weather], instance_name="weather-rag")
    stocks_out = dag.task(rag_stocks, [stocks], instance_name="stocks-rag")
    brewery_out = dag.task(brewery_task, [brewery], instance_name="brewery-rag")

    # dummy task for a single output. Seaplane does not yet support multiple outputs out of DAGs
    output = dag.task(
        dummy,
        [weather_out, stocks_out, other_out, brewery_out],
        instance_name="dummy",
    )

    # set the DAG response to the output
    dag.respond(output)

    # return the dag to the app
    return dag
