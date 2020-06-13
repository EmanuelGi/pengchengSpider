#!/usr/bin/env bash

if test $# -ne 1; then
    echo "Parameter: delete/create"
    exit 1
fi

if [ $1 = "delete" ]; then
    echo "delete index yls and plain"
    curl -XDELETE http://localhost:9200/yls
    curl -XDELETE http://localhost:9200/plain
elif [ $1 = 'create' ]; then
    echo "create index yls and plain"
    # TODO: load variable value from config.py
    curl -XPUT http://localhost:9200/yls -d'
    {
        "mappings": {
            "yls01" : {
                "properties" : {
                    "content" : {
                        "type" :    "text",
                        "analyzer": "ik_smart",
                        "search_analyzer": "ik_smart",
                        "term_vector": "with_positions_offsets"
                    },
                    "title" : {
                        "type" :    "text",
                        "analyzer": "ik_smart",
                        "search_analyzer": "ik_smart",
                        "term_vector": "with_positions_offsets"
                    },
                    "keywords" : {
                        "type" :    "text",
                        "analyzer": "ik_smart",
                        "search_analyzer": "ik_smart",
                        "term_vector": "with_positions_offsets"
                    },
                    "description" : {
                        "type" :    "text",
                        "analyzer": "ik_smart",
                        "search_analyzer": "ik_smart",
                        "term_vector": "with_positions_offsets"
                    }
                }
            }
        }
    }'
    curl -XPUT http://localhost:9200/plain01 -d'
    {
        "settings": {
            "similarity": {
                "my_sim": {
                    "type": "BM25",
                    "b":    0.75
                }
            }
        },
        "mappings": {
            "yls01" : {
                "properties" : {
                    "content" : {
                        "type" :    "text",
                        "analyzer": "ik_smart",
                        "search_analyzer": "ik_smart",
                        "term_vector": "with_positions_offsets",
                        "similarity": "my_sim"
                    },
                    "site_code" : {
                        "type" :   "long"
                    },
                    "title" : {
                        "type" :    "text",
                        "analyzer": "ik_smart",
                        "search_analyzer": "ik_smart",
                        "term_vector": "with_positions_offsets",
                        s"smilarity": "my_sim"
                    },
                    "keywords" : {
                        "type" :    "text",
                        "analyzer": "ik_smart",
                        "search_analyzer": "ik_smart",
                        "term_vector": "with_positions_offsets",
                        s"smilarity": "my_sim"
                    },
                    "description" : {
                        "type" :    "text",
                        "analyzer": "ik_smart",
                        "search_analyzer": "ik_smart",
                        "term_vector": "with_positions_offsets",
                        s"smilarity": "my_sim"
                    }
                }
            }
        }
    }'
    curl -XPUT http://localhost:9200/plain01/_alias/plain
fi


