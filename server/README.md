## TrainGenie

To create the train database, run:
```bash
./data_extractor.py --outfile ./train_data.json
```

To run the service:
```
./server.py --train_db ./train_data.json
```