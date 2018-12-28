# Jupyter-start
    A service for jupyter start with the system

    move it to /etc/systemd/system/

    '''systemctl enable jupyter.service'''

# steps for add new jupyter-start service

    1. add /etc/systemd/system/jupyter.service
    
    2. run systemctl enable jupyter.service
    
    3. in the jupyter path: jupyter-notebook --generate-config
    
    4. modify .jupyter/jupyter-config.py
    
    > ip = '*'
    > path = 'path/to/jupyter'
    > openbrowser = False
    > port = 1111
    
    5. jupyter-notebook password
    
    6. ufw allow 1111/tcp
    
    7. restart


# add user
    1. sudo adduser spurs
