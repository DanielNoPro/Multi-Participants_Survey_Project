import { questionService } from '@/services/questionService';
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const fetchGetQuestions = createAsyncThunk(
    'question/getQuestions',
    async (params) => {
        const res = await questionService.getQuestions(params.page, params.size);
        return res;
    }
);

export const fetchGetQuestionTypes = createAsyncThunk(
    'question/getQuestionTypes',
    async () => {
        const res = await questionService.getQuestionTypes();
        return res;
    }
);

const questionSlice = createSlice({
    name: 'question',
    initialState: {
        questions: [],
        loadingQuestion: false,
        questionTypes: [],
        modalQuestion: false,
        current: 1,
    },
    reducers: {
        setModalQuestion(state, { payload }) {
            state.modalQuestion = payload;
        },
        setCurrentPage(state, { payload }) {
            state.current = payload;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(
                fetchGetQuestions.pending, (state, action) => {
                    state.loadingQuestion = true
                }
            )
            .addCase(
                fetchGetQuestions.fulfilled, (state, action) => {
                    state.questions = action.payload
                    state.loadingQuestion = false
                }
            );
        builder.addCase(
            fetchGetQuestionTypes.fulfilled, (state, action) => {
                state.questionTypes = action.payload.data
            }
        );
    },
});

const { reducer, actions } = questionSlice;
export const {
    setModalQuestion,
    setCurrentPage
} = actions;

export default reducer;
