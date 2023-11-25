
def fail(project_id, response): 
    raise Exception(f'Project {project_id} failed to update. Reason: \n{response.status_code} - {response.text}')
