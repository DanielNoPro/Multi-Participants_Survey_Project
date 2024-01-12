import { surveyService } from '@/services/surveyService';
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const fetchGetSurveys = createAsyncThunk(
    'survey/getSurveys',
    async (page) => {
        const res = await surveyService.getSurveys(page);
        return res;
    }
);

export const fetchCreateSurvey = createAsyncThunk(
    'survey/createSurvey',
    async (data) => {
        const res = await surveyService.createSurvey(data);
        return res;
    }
);

export const fetchDeleteSurvey = createAsyncThunk(
    'survey/deleteSurvey',
    async (data) => {
        const res = await surveyService.deleteSurvey(data);
        return res;
    }
);

export const fetchUpdateSurvey = createAsyncThunk(
    'survey/updateSurvey',
    async (id, data) => {
        const res = await surveyService.updateSurvey(id, data);
        return res;
    }
);

export const fetchGetSurveyDetail = createAsyncThunk(
    'survey/getSurveyDetail',
    async (id) => {
        const res = await surveyService.getSurveyDetail(id);
        return res;
    }
);

export const fetchGetSurveyQuestions = createAsyncThunk(
    'survey/getSurveyQuestions',
    async (data) => {
        const res = await surveyService.getSurveyQuestions(data.id, data.page);
        return res;
    }
);

const surveySlice = createSlice({
    name: 'survey',
    initialState: {
        surveys: [],
        loadingSurvey: false,
        modalSurvey: false,
        surveyDetail: {},
        surveyQuestions: [],
    },
    reducers: {
        setModalSurvey(state, { payload }) {
            state.modalSurvey = payload;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(
                fetchGetSurveys.pending, (state, action) => {
                    state.loadingSurvey = true
                }
            )
            .addCase(
                fetchGetSurveys.fulfilled, (state, action) => {
                    state.surveys = action.payload
                    state.loadingSurvey = false
                }
            );
        builder
            .addCase(
                fetchGetSurveyDetail.pending, (state, action) => {
                    state.loadingSurvey = true
                }
            )
            .addCase(
                fetchGetSurveyDetail.fulfilled, (state, action) => {
                    state.surveyDetail = action.payload
                    state.loadingSurvey = false
                }
            );
        builder
            .addCase(
                fetchGetSurveyQuestions.pending, (state, action) => {
                    state.loadingSurvey = true
                }
            )
            .addCase(
                fetchGetSurveyQuestions.fulfilled, (state, action) => {
                    state.surveyQuestions = action.payload
                    state.loadingSurvey = false
                }
            );
    },
});

const { reducer, actions } = surveySlice;
export const {
    setModalSurvey,
} = actions;

export default reducer;
