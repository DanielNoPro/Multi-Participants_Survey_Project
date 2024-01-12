import { questionService } from '@/services/questionService';
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const fetchGetQuestions = createAsyncThunk(
    'question/getQuestions',
    async (page) => {
        const res = await questionService.getQuestions(page);
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
        modalQuestion: false
    },
    reducers: {
        setModalQuestion(state, { payload }) {
            state.modalQuestion = payload;
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
        )
    },
});

const { reducer, actions } = questionSlice;
export const {
    setModalQuestion,
} = actions;

export default reducer;
