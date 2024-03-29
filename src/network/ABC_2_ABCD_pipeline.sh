#!/bin/bash

#parse args, necessary args are 1. putative enhancers from ABC 2. fithic loop output (I'm pretty sure)
POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -e|--enhancers)
      ENHANCERS="$2"
      shift # past argument
      shift # past value
      ;;
    -l|--loops)
      LOOP_DIR="$2"
      shift # past argument
      shift # past value
      ;;
    -h|--hic)
      HIC_DIR="$3"
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

#echo "ENHANCERS  = ${ENHANCERS}"
#echo "LOOP_DIR     = ${LOOP_DIR}"

#start by creating a list of genes from enhancers
#cut ${ENHANCERS} -f2,8,9 | tail -n +2 | sort -k2 -k3 | uniq > data/gene_tss.uniq.tsv

#next create the base networks
#node01
#cat data/gene_parts.ab | cut -f2 | parallel --max-args=1 -j 35 'python src/generate_base_networks.py {1}' 

#node02
#cat data/gene_parts.aa1 | cut -f2 | parallel --max-args=1 -j 35 'python src/generate_base_networks.py {1}' 

#node03
#cat data/gene_parts.ac | cut -f2 | parallel --max-args=1 -j 35 'python src/generate_base_networks.py {1}' 

#filter the base networks 
#node01
#ls data/gene_tss_parts/ | parallel --max-args=1 -j 35 'python src/optimize_loop_pvalue.py data/enhancers.gas.class.tsv --gene_tss data/gene_tss_parts/{1}' 

#subroutine to gather ChIPSeq data and map it to a feature matrix we'll use to train the ML to predict true enhancers
#first create a bedfile from enhancers matrix 
#cut -f2,3,4 data/enhancers.gas.class.tsv | sort -k1 -k2 | uniq > data/enhancer_table.bed
#python src/create_enhancer_bed.py
#python src/create_chipseq_matrix.py




