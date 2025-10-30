#!/usr/bin/env python3
"""
Script para listar documentos processados pelo JURISRAG
"""

import os
import json
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

def print_header(message):
    """Print a header message"""
    print(f"{Style.BRIGHT}{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    print(f"{Style.BRIGHT}{Fore.CYAN}{message}{Style.RESET_ALL}")
    print(f"{Style.BRIGHT}{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")

def list_source_documents():
    """Lista todos os documentos .docx encontrados"""
    data_dir = "/Users/gabrielramos/Downloads/DRIVE_DO_BELISARIO"

    if not os.path.exists(data_dir):
        print(f"{Fore.RED}❌ Diretório não encontrado: {data_dir}{Style.RESET_ALL}")
        return

    print(f"{Fore.BLUE}ℹ️  Scanning directory: {data_dir}{Style.RESET_ALL}\n")

    # Find all .docx files
    docx_files = sorted(Path(data_dir).rglob("*.docx"))

    # Group by subdirectory
    grouped = {}
    for file in docx_files:
        # Get relative path from data_dir
        rel_path = file.relative_to(data_dir)
        # Get parent directory
        parent = str(rel_path.parent) if rel_path.parent != Path(".") else "Root"

        if parent not in grouped:
            grouped[parent] = []
        grouped[parent].append(rel_path.name)

    # Print summary
    print_header(f"📚 JURISRAG - Lista de Documentos")
    print()
    print(f"{Fore.GREEN}✅ Total de documentos encontrados: {len(docx_files)}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}ℹ️  Total de categorias: {len(grouped)}{Style.RESET_ALL}")
    print()

    # Print grouped files
    for category in sorted(grouped.keys()):
        files = grouped[category]
        print(f"{Style.BRIGHT}{Fore.CYAN}📁 {category}{Style.RESET_ALL} ({len(files)} arquivos)")
        for i, filename in enumerate(sorted(files), 1):
            print(f"   {i:3d}. {filename}")
        print()

    # Save to JSON
    output_file = "processed_documents.json"
    doc_list = {
        "data_directory": data_dir,
        "total_documents": len(docx_files),
        "total_categories": len(grouped),
        "generated_at": datetime.now().isoformat(),
        "categories": {}
    }

    for category, files in grouped.items():
        doc_list["categories"][category] = sorted(files)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(doc_list, f, ensure_ascii=False, indent=2)

    print(f"{Fore.GREEN}✅ Lista salva em: {output_file}{Style.RESET_ALL}")

def check_vectorstore_status():
    """Verifica se o vectorstore foi criado"""
    vectorstore_path = "vectorstore"

    print()
    print_header("📊 Status do Vectorstore")
    print()

    if os.path.exists(vectorstore_path):
        files = os.listdir(vectorstore_path)
        if files:
            total_size = sum(
                os.path.getsize(os.path.join(vectorstore_path, f))
                for f in files
                if os.path.isfile(os.path.join(vectorstore_path, f))
            )
            print(f"{Fore.GREEN}✅ Vectorstore criado{Style.RESET_ALL}")
            print(f"   📁 Localização: {vectorstore_path}/")
            print(f"   📄 Arquivos: {len(files)}")
            print(f"   💾 Tamanho total: {total_size / 1024 / 1024:.2f} MB")
        else:
            print(f"{Fore.YELLOW}⚠️  Vectorstore vazio{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Vectorstore não encontrado{Style.RESET_ALL}")
        print(f"   Execute 'python load.py' para criar o vectorstore")

def check_log_file():
    """Verifica o arquivo de log"""
    log_file = "jurisrag.log"

    print()
    print_header("📝 Status dos Logs")
    print()

    if os.path.exists(log_file):
        size = os.path.getsize(log_file)
        with open(log_file, 'r') as f:
            lines = f.readlines()

        print(f"{Fore.GREEN}✅ Arquivo de log encontrado{Style.RESET_ALL}")
        print(f"   📁 Localização: {log_file}")
        print(f"   📄 Linhas: {len(lines)}")
        print(f"   💾 Tamanho: {size / 1024:.2f} KB")

        # Show last few lines
        print(f"\n{Style.BRIGHT}Últimas 5 linhas do log:{Style.RESET_ALL}")
        for line in lines[-5:]:
            print(f"   {line.rstrip()}")
    else:
        print(f"{Fore.YELLOW}⚠️  Arquivo de log não encontrado{Style.RESET_ALL}")

if __name__ == "__main__":
    list_source_documents()
    check_vectorstore_status()
    check_log_file()
    print()
