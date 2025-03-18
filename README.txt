# Misinformation Detection in Telegram Groups using GNNs

## Overview
This repository contains the codebase for the thesis project: **Classifying News Domains Shared in Telegram Chat Groups as Misinformation using Graph Neural Networks (GNNs)**.

### Thesis Motivation
The spread of misinformation in online platforms, particularly semi-anonymous messaging platforms like Telegram, poses a significant societal challenge. This project models Telegram groups and shared URLs as a graph structure, where:
- **Nodes** represent domains grouped from URLs.
- **Edges** represent sharing patterns in Telegram chat groups.

The hypothesis: **Graph Neural Networks (GNNs) can outperform state-of-the-art methods in classifying domains into misinformation by leveraging graph structure.**

## Repository Structure

### 01 Preprocessing Codefiles
#### merge_URL_domain
Preprocessing script to merge URLs into their domains and filtering out Social Media domains.

#### train_test_split
Handles dataset partitioning into training and test sets and groups the URL-Chat matrix into a Domain-Chat matrix.

#### scraper
Scrapes the articles of the URL with selenium 

#### nlp_article
Creates embeddings of the articles with multilingual transformer model (paraphrase-multilingual-MiniLM-L12-v2)

#### feature_generation
Responsible for generating feature sets for nodes (domains), including metadata-based features.

#### network_validation
Application of bipartite configuration model (BiCM) in order to statistically validate node similarities.

#### topic_modeling_chat
Performs topic modeling on chat data with LDA and SentenceBERT to add contextual features

### 02 Baseline Models
#### MLP
Implementation of simple Multi-Layer Perceptron (MLP) classifiers as baseline for misinformation classification.

#### BERT_fine_tuning
Fine-tuning of multilingual BERT model on article content to serve as one of the reference classifiers.


### 03 GNN Models
### GCN_content_agnostic
Implementation of different GNN (GCN, GAT, GraphSAGE) with content-agnostic metadata

### GCN_embeddings
GNN that combines article embeddings and metadata as features

### GCN_hierarchical
Explores hierarchical GCN architectures, modeling Telegram chat structures at multiple levels, including chat information (topics).

### 04 Testing





