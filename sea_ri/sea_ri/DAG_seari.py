# import DAGs
from DAG_RAG import rag_dag

# import TASKS
from TASK_stt_pre_processing import speech_to_text_pre_processing
from TASK_post_rag import post_rag
from TASK_tts_pre_processing import text_to_speech_pre_processing
from TASK_tts_post_processing import text_to_speech_post_processing
from TASK_quick_answer_prepro import quick_answer_pp


def seari_dag(app, name, input):
    """
    Create a DAG (Directed Acyclic Graph) for the Seari app. An LLM powered RAG-enaabled voice assistant.

    Args:
        app (Application): The application object.
        name (str): The name of the DAG.
        input (Message): The input data.

    Returns:
        dag (DAG): The DAG instance.

    DAG Response:
        audio_file (Message) a JSON object containing the URL to the audio file.
    """
    # create new dag instance
    dag = app.dag(name)

    # pre-process the input and select speech to text model
    stt_model_params = dag.task(
        speech_to_text_pre_processing, [input], instance_name="stt-pre"
    )

    # create prompt for claude3
    quick_answer = dag.task(
        quick_answer_pp, [stt_model_params], instance_name="quick-answer"
    )

    # run through substation to extract RAG categories
    rag_cats = app.substation_dag("cat-dag", [stt_model_params])

    # run through rag DAG to retrieve relevant info
    rag_info = rag_dag(app, "rag-dag", rag_cats)

    # post processing RAG and create prompt and select model for QA
    rag_enriched_prompt = dag.task(post_rag, [rag_info], instance_name="rag-enr")

    # run through substation to answer question
    answer = app.substation_dag("sub-ans", [rag_enriched_prompt, quick_answer])

    # post processing and select model for speech to text
    tts_prompt = dag.task(
        text_to_speech_pre_processing, [answer], instance_name="tts-pre"
    )

    # run through substation to create speech form either the RAG enriched or the quick answer
    speech = app.substation_dag("sub-tts", [tts_prompt])

    # retrieve audio file name
    audio_file = dag.task(
        text_to_speech_post_processing, [speech], instance_name="tts-post"
    )

    # send output out of dag
    dag.respond(audio_file)

    return dag
