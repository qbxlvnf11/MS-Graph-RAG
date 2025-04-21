Docker Environment
=============

### - Docker Build

```
docker build -t rag_server .
```

### - Docker Run

```
docker run -it --gpus all --name rag_server_env --shm-size=64G -p {port}:{port} -e GRANT_SUDO=yes --user root -v {root_folder}:/workspace/rag_server -w /workspace/rag_server rag_server_env bash
```

### - Docker Exec

```
docker exec -it rag_server_env bash
```


Build RAG (Indexing)
=============

### - Initialization

```
python initialize.py --system_config_path {system_config_path}
```

### - Indexing
   - When using the GPT API, enter the API KEY in the '.env' file created after executing the initialization command
   - After creating an input folder in the generated project root folder, insert the original dataset to be used for rag indexing
   - Check for errors during indexing process: 'indexing-engine.log' file

```
python indexing.py --system_config_path {system_config_path}
```


Query
=============

### - Search
   - Search method options: 'local', 'global', ...

```
python run_query.py --system_config_path {system_config_path} --search_method {search_method} --query {query}
```


Web Test
=============

### - Run Chat Server

```
python chat_server.py --server_port {server_port} --rag_root_folder {rag_root_folder_path}
```

### - Run Client Server

```
python client_server.py --server_port {server_port} --client_port {client_port}
```