"""A module to collect shared logic."""

import streamlit as st
import os
from pathlib import Path
from honeybee.model import Model
from honeybee_vtk.model import Model as VTKModel
from ladybug.epw import EPW
from honeybee.model import Model as HBModel


@st.cache(hash_funcs={HBModel: lambda model: model.identifier})
def generate_vtkjs(here: Path, hb_model: Model) -> Path:
    directory = os.path.join(here.as_posix(), 'data', st.session_state.user_id)
    hbjson_path = hb_model.to_hbjson(hb_model.identifier, directory)
    vtk_model = VTKModel.from_hbjson(hbjson_path)
    return Path(vtk_model.to_vtkjs(folder=directory, name=hb_model.identifier))


def new_weather_file():
    st.session_state.sql_path = None
    st.session_state.rebuild_viz = True


def get_weather_file(here: Path):
    # upload weather file
    epw_file = st.file_uploader(
        'Upload a weather file (EPW)', type=['epw'], on_change=new_weather_file)
    if epw_file:
        # save EPW in data folder
        epw_path = Path(f'./{here}/data/{st.session_state.user_id}/{epw_file.name}')
        epw_path.parent.mkdir(parents=True, exist_ok=True)
        epw_path.write_bytes(epw_file.read())
        # create a DDY file from the EPW
        ddy_file = epw_path.as_posix().replace('.epw', '.ddy')
        epw_obj = EPW(epw_path.as_posix())
        epw_obj.to_ddy(ddy_file)
        ddy_path = Path(ddy_file)
        # set the session state variables
        st.session_state.epw_path = epw_path
        st.session_state.ddy_path = ddy_path
