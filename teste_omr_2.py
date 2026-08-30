import os

import json

import tkinter as tk

from tkinter import filedialog, messagebox

import cv2

import fitz

import numpy as np

from PIL import Image

from engine.geometria import (
    normalizar_com_diagnostico,
    obter_ids_referencia
)

from engine.omr import OMRReader


# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

DPI = 600

DIRETORIO_FICHAS = "fichas"

ARQUIVO_FICHA_ATIVA = os.path.join(
    DIRETORIO_FICHAS,
    "ativa.json"
)

DIRETORIO_TEMP = "temp"

MARGEM_OMR = 7


# ==========================================================
# TESTE OMR 2.0
# ==========================================================

class TesteOMR2:

    def __init__(
        self,
        root
    ):
        self.root = root

        self.root.title(
            "SDIP 2.0 - Teste OMR"
        )

        self.root.geometry(
            "1000x750"
        )

        self.mapa_path = None
        self.ficha_ativa_id = None

        self.criar_interface()

    # ======================================================
    # INTERFACE
    # ======================================================

    def criar_interface(
        self
    ):

        titulo = tk.Label(
            self.root,
            text="SDIP 2.0 - Teste de Leitura OMR",
            font=(
                "Segoe UI",
                20,
                "bold"
            )
        )

        titulo.pack(
            pady=(20, 5)
        )

        descricao = tk.Label(
            self.root,
            text=(
                "Selecione uma ficha PDF escaneada. "
                "O sistema utilizará automaticamente o "
                "mapa OMR da ficha ativa."
            ),
            font=(
                "Segoe UI",
                10
            )
        )

        descricao.pack(
            pady=(0, 15)
        )

        self.botao = tk.Button(
            self.root,
            text="Selecionar ficha PDF",
            command=self.selecionar_pdf,
            font=(
                "Segoe UI",
                11
            ),
            padx=20,
            pady=8
        )

        self.botao.pack(
            pady=10
        )

        self.status = tk.Label(
            self.root,
            text="Aguardando ficha...",
            font=(
                "Segoe UI",
                10
            )
        )

        self.status.pack(
            pady=10
        )

        # ==================================================
        # RESULTADOS
        # ==================================================

        frame_resultados = tk.Frame(
            self.root
        )

        frame_resultados.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        scrollbar = tk.Scrollbar(
            frame_resultados
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.resultados = tk.Text(
            frame_resultados,
            font=(
                "Consolas",
                10
            ),
            yscrollcommand=scrollbar.set
        )

        self.resultados.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.configure(
            command=self.resultados.yview
        )

    # ======================================================
    # DESCOBRIR FICHA ATIVA
    # ======================================================

    def obter_mapa_ficha_ativa(
        self
    ):

        if not os.path.isfile(
            ARQUIVO_FICHA_ATIVA
        ):
            raise FileNotFoundError(
                (
                    "Arquivo da ficha ativa não encontrado:\n\n"
                    f"{ARQUIVO_FICHA_ATIVA}\n\n"
                    "Crie ou defina uma ficha ativa no SDIP "
                    "antes de executar este teste."
                )
            )

        try:

            with open(
                ARQUIVO_FICHA_ATIVA,
                "r",
                encoding="utf-8"
            ) as arquivo:

                ativa = json.load(
                    arquivo
                )

        except (
            OSError,
            json.JSONDecodeError
        ) as erro:

            raise RuntimeError(
                (
                    "Não foi possível ler o arquivo "
                    "da ficha ativa.\n\n"
                    f"{erro}"
                )
            )

        ficha_id = ativa.get(
            "ficha_id"
        )

        if not ficha_id:

            raise ValueError(
                (
                    "O arquivo ativa.json não possui "
                    "um ficha_id válido."
                )
            )

        pasta_ficha = os.path.join(
            DIRETORIO_FICHAS,
            ficha_id
        )

        mapa_path = os.path.join(
            pasta_ficha,
            "mapa_omr.json"
        )

        if not os.path.isfile(
            mapa_path
        ):
            raise FileNotFoundError(
                (
                    "O mapa OMR da ficha ativa "
                    "não foi encontrado.\n\n"
                    f"{mapa_path}\n\n"
                    "Verifique se a ficha possui o "
                    "arquivo mapa_omr.json."
                )
            )

        return (
            ficha_id,
            os.path.abspath(
                mapa_path
            )
        )

    # ======================================================
    # SELECIONAR PDF
    # ======================================================

    def selecionar_pdf(
        self
    ):

        caminho = filedialog.askopenfilename(
            title="Selecionar ficha PDF escaneada",
            filetypes=[
                (
                    "Arquivos PDF",
                    "*.pdf"
                ),
                (
                    "Todos os arquivos",
                    "*.*"
                )
            ]
        )

        if not caminho:
            return

        self.botao.configure(
            state="disabled"
        )

        self.status.configure(
            text="Localizando ficha ativa e processando..."
        )

        self.resultados.delete(
            "1.0",
            "end"
        )

        self.root.update_idletasks()

        try:

            resultados = self.processar_pdf(
                caminho
            )

            self.mostrar_resultados(
                resultados
            )

            self.status.configure(
                text="Teste concluído."
            )

        except Exception as erro:

            self.status.configure(
                text="Erro durante o teste."
            )

            messagebox.showerror(
                "Erro",
                (
                    "Não foi possível executar "
                    "o teste.\n\n"
                    f"{erro}"
                )
            )

            print()

            print(
                "=" * 70
            )

            print(
                "ERRO"
            )

            print(
                "=" * 70
            )

            print(
                repr(erro)
            )

            print(
                "=" * 70
            )

        finally:

            self.botao.configure(
                state="normal"
            )

    # ======================================================
    # RENDERIZAR PÁGINA
    # ======================================================

    def renderizar_pagina(
        self,
        pagina
    ):

        escala = (
            DPI / 72.0
        )

        matriz = fitz.Matrix(
            escala,
            escala
        )

        pix = pagina.get_pixmap(
            matrix=matriz,
            alpha=False
        )

        imagem = np.frombuffer(
            pix.samples,
            dtype=np.uint8
        )

        imagem = imagem.reshape(
            pix.height,
            pix.width,
            pix.n
        )

        if pix.n == 3:

            imagem = cv2.cvtColor(
                imagem,
                cv2.COLOR_RGB2BGR
            )

        elif pix.n == 4:

            imagem = cv2.cvtColor(
                imagem,
                cv2.COLOR_RGBA2BGR
            )

        else:

            raise ValueError(
                (
                    "Formato de imagem "
                    "não suportado: "
                    f"{pix.n} canais."
                )
            )

        return imagem

    # ======================================================
    # PROCESSAR PÁGINA
    # ======================================================

    def processar_pagina(
        self,
        pagina_pdf,
        numero_pagina,
        total_paginas
    ):

        print()

        print(
            "=" * 70
        )

        print(
            f"PROCESSANDO PÁGINA "
            f"{numero_pagina}/{total_paginas}"
        )

        print(
            "=" * 70
        )

        # --------------------------------------------------
        # Renderização
        # --------------------------------------------------

        imagem = self.renderizar_pagina(
            pagina_pdf
        )

        print(
            f"Imagem original: "
            f"{imagem.shape[1]} x "
            f"{imagem.shape[0]}"
        )

        print(
            f"DPI utilizado: {DPI}"
        )

        # --------------------------------------------------
        # IDs esperados desta página
        # --------------------------------------------------

        ids_esperados = sorted(
            obter_ids_referencia(
                numero_pagina
            )
        )

        print(
            f"IDs ArUco esperados: "
            f"{ids_esperados}"
        )

        # --------------------------------------------------
        # Geometria
        # --------------------------------------------------

        self.status.configure(
            text=(
                f"Página {numero_pagina}/"
                f"{total_paginas}: "
                "detectando ArUcos..."
            )
        )

        self.root.update_idletasks()

        (
            imagem_normalizada,
            imagem_diagnostico,
            pontos,
            matriz
        ) = normalizar_com_diagnostico(
            imagem,
            pagina=numero_pagina
        )

        # --------------------------------------------------
        # Mostrar pontos
        # --------------------------------------------------

        print()

        print(
            "ARUCOS ENCONTRADOS"
        )

        print(
            "--------------------------------------"
        )

        for posicao in range(4):

            if posicao not in pontos:

                raise ValueError(
                    (
                        f"Posição ArUco {posicao} "
                        f"não foi encontrada na "
                        f"página {numero_pagina}."
                    )
                )

            dados = pontos[
                posicao
            ]

            cx, cy = (
                dados["centro"]
            )

            id_real = dados[
                "id"
            ]

            print(
                f"Posição {posicao} | "
                f"ID {id_real}: "
                f"({cx:.2f}, {cy:.2f})"
            )

        print(
            "--------------------------------------"
        )

        print()

        print(
            "Imagem normalizada:"
        )

        print(
            f"{imagem_normalizada.shape[1]} x "
            f"{imagem_normalizada.shape[0]}"
        )

        # --------------------------------------------------
        # Salvar diagnóstico
        # --------------------------------------------------

        os.makedirs(
            DIRETORIO_TEMP,
            exist_ok=True
        )

        caminho_normalizada = os.path.join(
            DIRETORIO_TEMP,
            (
                f"omr2_pagina_"
                f"{numero_pagina}_normalizada.png"
            )
        )

        caminho_diagnostico = os.path.join(
            DIRETORIO_TEMP,
            (
                f"omr2_pagina_"
                f"{numero_pagina}_geometria.png"
            )
        )

        cv2.imwrite(
            caminho_normalizada,
            imagem_normalizada
        )

        cv2.imwrite(
            caminho_diagnostico,
            imagem_diagnostico
        )

        # --------------------------------------------------
        # OMR
        # --------------------------------------------------

        self.status.configure(
            text=(
                f"Página {numero_pagina}/"
                f"{total_paginas}: "
                "executando OMR..."
            )
        )

        self.root.update_idletasks()

        omr = OMRReader(
            mapa_path=self.mapa_path,
            margem=MARGEM_OMR
        )

        # --------------------------------------------------
        # BGR -> RGB
        # --------------------------------------------------

        imagem_rgb = cv2.cvtColor(
            imagem_normalizada,
            cv2.COLOR_BGR2RGB
        )

        imagem_pil = Image.fromarray(
            imagem_rgb
        )

        # --------------------------------------------------
        # Analisar SOMENTE a página atual
        # --------------------------------------------------

        resultados_pagina = omr.analisar_imagem(
            imagem_pil,
            pagina=numero_pagina
        )

        total = len(
            resultados_pagina
        )

        marcadas = sum(
            1
            for resultado in resultados_pagina
            if resultado["marcada"]
        )

        vazias = (
            total
            - marcadas
        )

        print()

        print(
            f"RESULTADO DA PÁGINA "
            f"{numero_pagina}"
        )

        print(
            f"Total de caixas: {total}"
        )

        print(
            f"Marcadas: {marcadas}"
        )

        print(
            f"Vazias: {vazias}"
        )

        return {
            "pagina": numero_pagina,
            "total": total,
            "marcadas": marcadas,
            "vazias": vazias,
            "resultados": resultados_pagina,
            "normalizada": caminho_normalizada,
            "diagnostico": caminho_diagnostico
        }

    # ======================================================
    # PROCESSAR PDF
    # ======================================================

    def processar_pdf(
        self,
        caminho
    ):

        # --------------------------------------------------
        # Descobrir ficha ativa
        # --------------------------------------------------

        (
            ficha_id,
            mapa_path
        ) = self.obter_mapa_ficha_ativa()

        self.ficha_ativa_id = ficha_id
        self.mapa_path = mapa_path

        # --------------------------------------------------
        # Carregar mapa
        # --------------------------------------------------

        with open(
            self.mapa_path,
            "r",
            encoding="utf-8"
        ) as arquivo:

            mapa = json.load(
                arquivo
            )

        quantidade_caixas = len(
            mapa.get(
                "coordenadas",
                []
            )
        )

        quantidade_paginas_mapa = mapa.get(
            "quantidade_paginas"
        )

        print()

        print(
            "=" * 70
        )

        print(
            "SDIP 2.0 - TESTE OMR"
        )

        print(
            "=" * 70
        )

        print(
            f"PDF: "
            f"{os.path.abspath(caminho)}"
        )

        print(
            f"Ficha ativa: "
            f"{self.ficha_ativa_id}"
        )

        print(
            f"Mapa: "
            f"{self.mapa_path}"
        )

        print(
            "Caixas no mapa: "
            f"{quantidade_caixas}"
        )

        print(
            "Páginas no mapa: "
            f"{quantidade_paginas_mapa}"
        )

        print(
            f"Margem OMR: "
            f"{MARGEM_OMR}"
        )

        print(
            "Limiar OMR: 5.0%"
        )

        print(
            "=" * 70
        )

        documento = fitz.open(
            caminho
        )

        try:

            total_paginas = (
                documento.page_count
            )

            if total_paginas <= 0:

                raise ValueError(
                    "O PDF não possui páginas."
                )

            # --------------------------------------------------
            # Validar PDF x mapa
            # --------------------------------------------------

            if (
                quantidade_paginas_mapa
                != total_paginas
            ):

                raise ValueError(
                    (
                        "A quantidade de páginas do PDF "
                        "não corresponde ao mapa da ficha ativa.\n\n"
                        f"PDF: {total_paginas}\n"
                        f"Mapa: {quantidade_paginas_mapa}\n\n"
                        f"Ficha ativa: {self.ficha_ativa_id}\n"
                        "Certifique-se de que o PDF escaneado "
                        "foi gerado a partir desta ficha."
                    )
                )

            resultados_paginas = []

            for indice in range(
                total_paginas
            ):

                numero_pagina = (
                    indice + 1
                )

                resultado = (
                    self.processar_pagina(
                        documento[indice],
                        numero_pagina,
                        total_paginas
                    )
                )

                resultados_paginas.append(
                    resultado
                )

            return resultados_paginas

        finally:

            documento.close()

    # ======================================================
    # MOSTRAR RESULTADOS
    # ======================================================

    def mostrar_resultados(
        self,
        resultados_paginas
    ):

        self.resultados.delete(
            "1.0",
            "end"
        )

        total_paginas = len(
            resultados_paginas
        )

        total_caixas = sum(
            pagina["total"]
            for pagina in resultados_paginas
        )

        total_marcadas = sum(
            pagina["marcadas"]
            for pagina in resultados_paginas
        )

        total_vazias = sum(
            pagina["vazias"]
            for pagina in resultados_paginas
        )

        # ==================================================
        # RESUMO
        # ==================================================

        self.resultados.insert(
            "end",
            "=" * 70
            + "\n"
        )

        self.resultados.insert(
            "end",
            "RESULTADO SDIP 2.0\n"
        )

        self.resultados.insert(
            "end",
            "=" * 70
            + "\n\n"
        )

        self.resultados.insert(
            "end",
            f"Ficha ativa: "
            f"{self.ficha_ativa_id}\n"
        )

        self.resultados.insert(
            "end",
            f"Mapa utilizado:\n"
            f"{self.mapa_path}\n\n"
        )

        self.resultados.insert(
            "end",
            f"Páginas processadas: "
            f"{total_paginas}\n"
        )

        self.resultados.insert(
            "end",
            f"Total de caixas: "
            f"{total_caixas}\n"
        )

        self.resultados.insert(
            "end",
            f"Marcadas: "
            f"{total_marcadas}\n"
        )

        self.resultados.insert(
            "end",
            f"Vazias: "
            f"{total_vazias}\n\n"
        )

        # ==================================================
        # RESULTADO POR PÁGINA
        # ==================================================

        for pagina in resultados_paginas:

            self.resultados.insert(
                "end",
                "-" * 70
                + "\n"
            )

            self.resultados.insert(
                "end",
                f"PÁGINA {pagina['pagina']}\n"
            )

            self.resultados.insert(
                "end",
                "-" * 70
                + "\n"
            )

            self.resultados.insert(
                "end",
                f"Total: "
                f"{pagina['total']}\n"
            )

            self.resultados.insert(
                "end",
                f"Marcadas: "
                f"{pagina['marcadas']}\n"
            )

            self.resultados.insert(
                "end",
                f"Vazias: "
                f"{pagina['vazias']}\n\n"
            )

            for resultado in pagina[
                "resultados"
            ]:

                nome = resultado[
                    "nome"
                ]

                percentual = resultado[
                    "percentual_escuro"
                ]

                marcada = resultado[
                    "marcada"
                ]

                estado = (
                    "MARCADA"
                    if marcada
                    else "VAZIA"
                )

                linha = (
                    f"{nome:<35} "
                    f"{percentual:>7.2f}%   "
                    f"{estado}\n"
                )

                self.resultados.insert(
                    "end",
                    linha
                )

        # ==================================================
        # TERMINAL
        # ==================================================

        print()

        print(
            "=" * 70
        )

        print(
            "RESUMO FINAL SDIP 2.0"
        )

        print(
            "=" * 70
        )

        print(
            f"Ficha ativa: "
            f"{self.ficha_ativa_id}"
        )

        print(
            f"Mapa: "
            f"{self.mapa_path}"
        )

        print(
            f"Páginas processadas: "
            f"{total_paginas}"
        )

        print(
            f"Total de caixas: "
            f"{total_caixas}"
        )

        print(
            f"Marcadas: "
            f"{total_marcadas}"
        )

        print(
            f"Vazias: "
            f"{total_vazias}"
        )

        print(
            "=" * 70
        )


# ==========================================================
# INICIALIZAÇÃO
# ==========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = TesteOMR2(
        root
    )

    root.mainloop()