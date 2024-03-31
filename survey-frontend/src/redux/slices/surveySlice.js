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
    async (data, {rejectWithValue}) => {
        return apiUser.post('/api/v1/token/redirect', data)
            .then((response) => {
                return response.data
            })
            .catch((err) => {
                throw rejectWithValue(err.response.data.detail)
            });
    }
)

export const fetchGetSurveyStatistics = createAsyncThunk(
    'survey/getSurveyStatistics',
    async (data) => {
        const res = await surveyService.getSurveyStatistics(data.id, data.page, data.page_size);
        return res;
    }
);

export const fetchGetSurveyParticipants = createAsyncThunk(
    'survey/getSurveyParticipants',
    async (data) => {
        const res = await surveyService.getSurveyParticipants(data.id, data.page);
        return res;
    }
);


export const fetchGetQuestionSets = createAsyncThunk(
    'survey/getQuestionSets',
    async (params) => {
        const res = await surveyService.getQuestionSets(params.id, params.page, params.size);
        return res;
    }
);

export const fetchGetSetPreConditions = createAsyncThunk(
    'survey/getSetPreConditions',
    async (params) => {
        const res = await surveyService.getSetPreConditions(params.survey_id, params.set_id);
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
        statistics: [],
        participants: {},
        current: 1,
        sets: {},
        setConditions: [],
        surveyErrors: ""
    },
    reducers: {
        setModalSurvey(state, { payload }) {
            state.modalSurvey = payload;
        },
        setCurrentPage(state, { payload }) {
            state.current = payload;
        },
        updateUserSurvey(state, { payload }) {
            state.userSurvey = payload;
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
            )
            .addCase(
                fetchGetUserSurveyQuestions.rejected, (state, action) => {
                    state.surveyErrors = action.payload
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
                    state.statistics = action.payload
                    state.loadingSurvey = false
                }
            );
        builder
            .addCase(
                fetchGetSurveyParticipants.pending, (state, action) => {
                    state.loadingSurvey = true
                }
            )
            .addCase(
                fetchGetSurveyParticipants.fulfilled, (state, action) => {
                    state.participants = action.payload
                    state.loadingSurvey = false
                }
            );
        builder
            .addCase(
                fetchGetQuestionSets.fulfilled, (state, action) => {
                    state.sets = action.payload
                }
            );
        builder
            .addCase(
                fetchGetSetPreConditions.fulfilled, (state, action) => {
                    state.setConditions = action.payload.data
                }
            )
    },
});

const { reducer, actions } = surveySlice;
export const {
    setModalSurvey,
    setCurrentPage,
    updateUserSurvey
} = actions;

export default reducer;
