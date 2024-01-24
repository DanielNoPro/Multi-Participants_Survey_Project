import { apiUser } from '@/constants/api';
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

export const fetchGetUserSurveyQuestions = createAsyncThunk(
    'survey/getUserSurveyQuestions',
    async (data) => {
        return apiUser.post('/api/v1/token/redirect', data)
            .then((response) => {
                return response.data
            })
            .catch((err) => {
                console.log(err);
            });
    }
)

export const fetchGetSurveyStatistics = createAsyncThunk(
    'survey/getSurveyStatistics',
    async (id) => {
        const res = await surveyService.getSurveyStatistics(id);
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
        userSurvey: {},
        statistics: []
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
        builder
            .addCase(
                fetchGetUserSurveyQuestions.pending, (state, action) => {
                    state.userSurvey = true
                }
            )
            .addCase(
                fetchGetUserSurveyQuestions.fulfilled, (state, action) => {
                    state.userSurvey = action.payload
                    state.loadingSurvey = false
                }
            );
        builder
            .addCase(
                fetchGetSurveyStatistics.pending, (state, action) => {
                    state.loadingSurvey = true
                }
            )
            .addCase(
                fetchGetSurveyStatistics.fulfilled, (state, action) => {
                    state.statistics = action.payload.data
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
