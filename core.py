from langchain import OpenAI
# from langchain.chains import SQLDatabaseSequentialChain
from langchain_experimental.sql import SQLDatabaseChain
from langchain.utilities import SQLDatabase
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
import cx_Oracle

# import mysql.connector
# import pymysql
# from mysql.connector import Error
# from sqlalchemy import create_engine,text
# from sqlalchemy.orm import sessionmaker


# username = 'jackson'
# password = 'j1#2c3K4'
# database_name = "sample" # Replace with your database name
# host = 'localhost'  # Replace with your database host
# host = 'relational.fit.cvut.cz'
# username = 'guest'
# password = 'relational'
# database_name = 'classicmodels'


def model(host, username, password, database_name, selectedTables):
    os.environ["OPENAI_API_KEY"] = "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"

    url = f"mysql+pymysql://{username}:{password}@{host}/{database_name}"
    db = SQLDatabase.from_uri(url, include_tables=selectedTables)
    llm = OpenAI(temperature=0, verbose=True)
    # llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k", verbose=False, max_tokens =500)

    db_chain = SQLDatabaseChain.from_llm(
        llm, db, verbose=False, use_query_checker=False, return_intermediate_steps=True
    )

    return db_chain,db

def model_postgres(host, username, password, database_name, selectedTables):
    os.environ["OPENAI_API_KEY"] = "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"

    # Create the PostgreSQL connection URL
    url = f"postgresql+psycopg2://{username}:{password}@{host}/{database_name}"

    # Connect to the database and include selected tables
    db = SQLDatabase.from_uri(url, include_tables=selectedTables)

    # Create an instance of the language model
    llm = OpenAI(temperature=0, verbose=True)

    # Create a sequential chain for database interaction
    db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=False, use_query_checker=False, return_intermediate_steps=True)

    return db_chain,db


def model_oracle(username, password, selected_tables):
    os.environ["OPENAI_API_KEY"] = "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"

    # Create a DSN for the Oracle database connection
    url = f'oracle+cx_oracle://{username}:{password}@localhost:1521/orcl'

    # Create an SQLDatabase instance from the connection
    db = SQLDatabase.from_uri(url, include_tables=selected_tables)
    
    # Create an OpenAI instance
    llm = OpenAI(temperature=0, verbose=True)

    # Create a chain between the language model and the database
    db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=False, use_query_checker=False, return_intermediate_steps=True)

    return db_chain,db
# test = model_oracle("system", "1234", [("logmnr_partobj$","logmnrc_gtcs")])

# Example usage

def get_generated_prompt(db_details,message):
    os.environ["OPENAI_API_KEY"] = "sk-zV6pGTCAjvo9KHact0SYT3BlbkFJFivKp94DrLWO9t99"

    db = db_details
    _DEFAULT_TEMPLATE = """
            All your responses must be based on provided text content .\
            Do not make up on your own.


            Given an input question, first create a syntactically correct {dialect} query to run, 
            then look at the results of the query and return the answer.

            Only use the following tables:

            {table_info}

            Double check the {dialect} query above for common mistakes, including:
            - Limit the float numbers in the answer upto 2 decimal places
            - Handling case sensitivity, e.g. using ILIKE instead of LIKE
            - Ensuring the join columns are correct
            - Casting values to the appropriate type
            - Apply the filters properly whenever required
            - Use units like thousands (K), Lacks (L) if numbers are big


            Rewrite the query here if there are any mistakes. If it looks good as it is, just reproduce the original query.


            Question: {input}"""

    prompt = PromptTemplate.from_template(
        template=_DEFAULT_TEMPLATE
    )
    input_variables = dict(input=message, table_info=db.get_usable_table_names(), dialect=db.dialect)
    generated_prompt = prompt.format(**input_variables)
    
    print(generated_prompt)
    return generated_prompt

    
    