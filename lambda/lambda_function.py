from generate import generate_data
from stage import stage_data

def lambda_handler(event, context):
    generate_data()
    stage_data()
    return 'success'
