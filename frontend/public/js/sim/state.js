/**
 * 牛顿环仿真状态管理
 * 使用 localStorage 实现跨窗口状态同步
 * 全局挂载为 window.simState
 */

(function() {
    const STATE_KEY = 'newtonSimState';

    const defaultState = {
        R: 1.0,
        lam: 589.3e-9,
        currentLevel: 0,
        maxLevel: 50,
        powerOn: false,
        reflectorAngle: 0,
        newtonPlaced: false,
        eyepieceIndex: 0,
        brightnessLevel: 0,
        offset: 0,
        taskStates: [0, 0, 0, 0, 0, 0]
    };

    function initState() {
        if (!localStorage.getItem(STATE_KEY)) {
            const state = {
                ...defaultState,
                R: Math.random() * 1.2 + 0.8
            };
            localStorage.setItem(STATE_KEY, JSON.stringify(state));
            console.log('初始化仿真参数，曲率半径 R =', state.R.toFixed(4), 'm');
        }
    }

    function getState() {
        const stored = localStorage.getItem(STATE_KEY);
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch (e) {
                console.error('状态解析错误:', e);
                return { ...defaultState };
            }
        }
        return { ...defaultState };
    }

    function getStateValue(key) {
        return getState()[key];
    }

    function setState(key, value) {
        const state = getState();
        state[key] = value;
        localStorage.setItem(STATE_KEY, JSON.stringify(state));
    }

    function setStateMulti(updates) {
        const state = getState();
        Object.assign(state, updates);
        localStorage.setItem(STATE_KEY, JSON.stringify(state));
    }

    function resetState() {
        const state = {
            ...defaultState,
            R: Math.random() * 1.2 + 0.8
        };
        localStorage.setItem(STATE_KEY, JSON.stringify(state));
    }

    function onStateChange(callback) {
        window.addEventListener('storage', (e) => {
            if (e.key === STATE_KEY) {
                try {
                    const newState = JSON.parse(e.newValue);
                    callback(newState);
                } catch (err) {
                    console.error('状态变化解析错误:', err);
                }
            }
        });
    }

    function canShowRings() {
        const state = getState();
        return state.powerOn && state.newtonPlaced && state.reflectorAngle === 1;
    }

    function updateTaskState(taskIndex, completed) {
        const state = getState();
        state.taskStates[taskIndex] = completed ? 1 : 0;
        localStorage.setItem(STATE_KEY, JSON.stringify(state));
    }

    function getInstrumentImage() {
        const state = getState();
        if (state.newtonPlaced && state.powerOn) return 'T-O.webp';
        if (state.newtonPlaced && !state.powerOn) return 'T-C.webp';
        if (!state.newtonPlaced && state.powerOn) return 'F-O.webp';
        return 'F-C.webp';
    }

    window.simState = {
        initState,
        getState,
        getStateValue,
        setState,
        setStateMulti,
        resetState,
        onStateChange,
        canShowRings,
        updateTaskState,
        getInstrumentImage
    };
})();
